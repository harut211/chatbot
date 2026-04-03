import json
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from service.prompt import GeminiService

from .models import Reservation, Room


try:
    ai_service = GeminiService()
    startup_error = ""
except Exception as exc:
    ai_service = None
    startup_error = str(exc)


def home(request):
    room_qs = Room.objects.filter(is_available=True).order_by("price_per_night")
    rooms = [
        {
            "name": f"{room.room_type} (Room {room.room_number})",
            "price": f"${room.price_per_night}/night",
            "desc": f"Capacity: {room.capacity} guests",
        }
        for room in room_qs
    ]
    return render(request, "hotel/index.html", {"rooms": rooms})


def _detect_language(message: str) -> str:
    if re.search(r"[\u0530-\u058F]", message):
        return "hy"
    if re.search(r"[\u0400-\u04FF]", message):
        return "ru"
    return "en"


def _t(lang: str, key: str) -> str:
    translations = {
        "en": {
            "method_not_allowed": "Method not allowed",
            "ai_unavailable": "AI service unavailable",
            "message_required": "message is required",
            "reserve_missing": "To reserve a room, please provide: {fields}.",
            "past_date": "Check-in date cannot be in the past. Please provide a future date.",
            "room_not_found": "Room {room} does not exist. Please choose another room.",
            "room_unavailable": "Room {room} is currently unavailable. Please choose another room.",
            "booking_confirmed": "Reservation confirmed. Booking ID: {id}. Room {room} for {guest}, check-in {check_in}, {nights} night(s), total ${total}.",
            "failed_generate": "Failed to generate response: {error}",
            "no_rooms": "No rooms are currently available.",
        },
        "hy": {
            "method_not_allowed": "Մեթոդը թույլատրված չէ",
            "ai_unavailable": "AI ծառայությունը հասանելի չէ",
            "message_required": "message դաշտը պարտադիր է",
            "reserve_missing": "Սենյակ ամրագրելու համար նշեք՝ {fields}։",
            "past_date": "Մուտքի ամսաթիվը չի կարող լինել անցյալում։ Նշեք ապագա ամսաթիվ։",
            "room_not_found": "{room} համարի սենյակը գոյություն չունի։ Ընտրեք այլ սենյակ։",
            "room_unavailable": "{room} համարի սենյակը այժմ հասանելի չէ։ Ընտրեք այլ սենյակ։",
            "booking_confirmed": "Ամրագրումը հաստատված է։ Ամրագրման ID՝ {id}։ Սենյակ {room}, հյուր՝ {guest}, մուտք՝ {check_in}, {nights} գիշեր, ընդհանուր՝ ${total}։",
            "failed_generate": "Պատասխանի գեներացումը ձախողվեց՝ {error}",
            "no_rooms": "Այս պահին հասանելի սենյակներ չկան։",
        },
        "ru": {
            "method_not_allowed": "Метод не разрешен",
            "ai_unavailable": "AI сервис недоступен",
            "message_required": "поле message обязательно",
            "reserve_missing": "Чтобы забронировать номер, укажите: {fields}.",
            "past_date": "Дата заезда не может быть в прошлом. Укажите будущую дату.",
            "room_not_found": "Номер {room} не существует. Выберите другой номер.",
            "room_unavailable": "Номер {room} сейчас недоступен. Выберите другой номер.",
            "booking_confirmed": "Бронирование подтверждено. ID брони: {id}. Номер {room} для {guest}, заезд {check_in}, {nights} ноч(и), итог ${total}.",
            "failed_generate": "Не удалось сгенерировать ответ: {error}",
            "no_rooms": "Сейчас нет доступных номеров.",
        },
    }
    return translations.get(lang, translations["en"]).get(key, key)


def _extract_budget(message: str):
    budget_patterns = [
        r"(?:\$|usd\s*)(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*\$",
        r"(?:մինչև|մինչեւ|budget|under|max|up to|до)\s*(\d+(?:\.\d+)?)",
    ]
    for pattern in budget_patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            try:
                return Decimal(match.group(1))
            except (InvalidOperation, ValueError):
                pass

    numbers = re.findall(r"\d+(?:\.\d+)?", message)
    if not numbers:
        return None
    try:
        return max(Decimal(n) for n in numbers)
    except (InvalidOperation, ValueError):
        return None


def _extract_client_count(message: str):
    match = re.search(
        r"(\d+)\s*(?:people|persons|guests|clients|հյուր(?:ի)?|մարդ|человек|чел|гост)",
        message,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    try:
        return max(1, int(match.group(1)))
    except ValueError:
        return None


def _extract_reservation_data(message: str):
    room_match = re.search(r"(?:room|սենյակ|номер)\s*#?\s*(\w+)", message, flags=re.IGNORECASE)
    name_match = re.search(
        r"(?:name is|for|անունը|имя)\s+([A-Za-z\u0530-\u058F\u0400-\u04FF][A-Za-z\u0530-\u058F\u0400-\u04FF\s'-]{1,60})",
        message,
        flags=re.IGNORECASE,
    )
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", message)
    nights_match = re.search(r"(\d+)\s*(?:nights?|գիշեր|ноч)", message, flags=re.IGNORECASE)

    room_number = room_match.group(1) if room_match else None
    guest_name = name_match.group(1).strip() if name_match else None
    check_in_raw = date_match.group(1) if date_match else None
    nights = int(nights_match.group(1)) if nights_match else 1

    check_in_date = None
    if check_in_raw:
        try:
            check_in_date = datetime.strptime(check_in_raw, "%Y-%m-%d").date()
        except ValueError:
            check_in_date = None

    return {
        "room_number": room_number,
        "guest_name": guest_name,
        "check_in_date": check_in_date,
        "nights": max(1, nights),
    }


def _is_booking_intent(message: str) -> bool:
    booking_keywords = ["book", "reserve", "reservation", "booking", "ամրագր", "брон", "заброни"]
    lower_msg = message.lower()
    return any(word in lower_msg for word in booking_keywords)


def _try_create_reservation(message: str, lang: str):
    data = _extract_reservation_data(message)
    missing = []
    if not data["room_number"]:
        missing.append("room number / սենյակի համար / номер")
    if not data["guest_name"]:
        missing.append("guest name / հյուրի անուն / имя гостя")
    if not data["check_in_date"]:
        missing.append("check-in date YYYY-MM-DD")

    if missing:
        return {"ok": False, "response": _t(lang, "reserve_missing").format(fields=", ".join(missing))}

    if data["check_in_date"] < date.today():
        return {"ok": False, "response": _t(lang, "past_date")}

    try:
        room = Room.objects.get(room_number=data["room_number"])
    except Room.DoesNotExist:
        return {"ok": False, "response": _t(lang, "room_not_found").format(room=data["room_number"])}

    if not room.is_available:
        return {"ok": False, "response": _t(lang, "room_unavailable").format(room=room.room_number)}

    total_price = room.price_per_night * data["nights"]
    reservation = Reservation.objects.create(
        room=room,
        guest_name=data["guest_name"],
        check_in_date=data["check_in_date"],
        nights=data["nights"],
        total_price=total_price,
    )

    room.is_available = False
    room.save(update_fields=["is_available"])

    return {
        "ok": True,
        "response": _t(lang, "booking_confirmed").format(
            id=reservation.id,
            room=room.room_number,
            guest=reservation.guest_name,
            check_in=reservation.check_in_date,
            nights=reservation.nights,
            total=reservation.total_price,
        ),
    }


def _room_inventory_context(user_message: str, lang: str) -> str:
    all_available = list(Room.objects.filter(is_available=True).order_by("price_per_night"))
    if not all_available:
        return _t(lang, "no_rooms")

    budget = _extract_budget(user_message)
    clients = _extract_client_count(user_message)

    filtered = all_available
    if clients is not None:
        filtered = [room for room in filtered if room.capacity >= clients]
    if budget is not None:
        filtered = [room for room in filtered if room.price_per_night <= budget]

    available_lines = [
        f"- Room {room.room_number}: {room.room_type}, capacity {room.capacity}, ${room.price_per_night}/night"
        for room in all_available
    ]
    context_parts = [
        "Current available rooms from database:",
        "\n".join(available_lines),
    ]

    if clients is not None:
        context_parts.append(f"Clients detected: {clients}")
    if budget is not None:
        context_parts.append(f"Budget detected: ${budget}")

    if filtered:
        suggestion_lines = [
            f"- Room {room.room_number}: {room.room_type}, capacity {room.capacity}, ${room.price_per_night}/night"
            for room in filtered[:5]
        ]
        context_parts.extend(
            [
                "Best matching rooms based on request:",
                "\n".join(suggestion_lines),
            ]
        )
    elif clients is not None or budget is not None:
        context_parts.append("No room matches the requested price/client count exactly. Suggest closest alternatives.")

    return "\n\n".join(context_parts)


@csrf_exempt
def assistant_chat(request):
    if request.method != "POST":
        return JsonResponse({"detail": _t("en", "method_not_allowed")}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
        message = (payload.get("message") or "").strip()
        lang = _detect_language(message)

        if ai_service is None:
            return JsonResponse({"detail": f"{_t(lang, 'ai_unavailable')}: {startup_error}"}, status=500)

        if not message:
            return JsonResponse({"detail": _t(lang, "message_required")}, status=400)

        if _is_booking_intent(message):
            booking_result = _try_create_reservation(message, lang)
            return JsonResponse({"response": booking_result["response"]})

        room_context = _room_inventory_context(message, lang)
        language_map = {"hy": "Armenian", "ru": "Russian", "en": "English"}
        target_language = language_map.get(lang, "English")

        grounded_prompt = ai_service.build_grounded_prompt(room_context, message, target_language)

        response = ai_service.generate_response(grounded_prompt)
        return JsonResponse({"response": response})
    except Exception as exc:
        return JsonResponse({"detail": _t("en", "failed_generate").format(error=exc)}, status=500)
