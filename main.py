# main.py
import os
import json
import telebot
from fastapi import FastAPI, Request, Response
import uvicorn
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, ADMIN_ID, APP_URL
from logs import logger
from database import init_db, SessionLocal, User
from keyboards import (
    main_keyboard, search_type_keyboard, course_kind_keyboard,
    categories_keyboard, confirm_search_keyboard, confirm_upload_keyboard,
    points_packages_keyboard, payment_confirm_keyboard, admin_keyboard
)
from points import get_or_create_user, get_points, deduct_points, add_points
from user_service import register_user, add_favorite, get_favorites
from search_service import search_courses
from uploader import create_upload
from admin import notify_admin
from maintenance import is_active, enable, disable

# Init DB
init_db()

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()

# In-memory sessions (works for single-instance, okay on Render single instance)
TEMP = {}

@app.on_event("startup")
async def startup_event():
    # set webhook
    try:
        bot.remove_webhook()
    except Exception:
        pass
    try:
        bot.set_webhook(url=WEBHOOK_URL)
        logger.info("Webhook set to %s", WEBHOOK_URL)
    except Exception as e:
        logger.exception("Failed to set webhook: %s", e)

@app.post(WEBHOOK_PATH)
async def webhook_endpoint(request: Request):
    if is_active():
        # return maintenance message silently
        return Response(status_code=200, content="maintenance")
    body = await request.body()
    json_str = body.decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return Response(status_code=200)

# Handlers using telebot decorator style
@bot.message_handler(commands=["start"])
def handle_start(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username
    # check referral code
    text = msg.text or ""
    parts = text.split()
    ref = None
    if len(parts) > 1 and parts[1].startswith("ref"):
        try:
            ref = int(parts[1][3:])
        except:
            ref = None
    register_user(user_id, username=username, invited_by=ref)
    kb = main_keyboard()
    bot.send_message(user_id,
        "مرحبًا بك في بوت 'كورسات مجانية ومدفوعة' 🎓\nاختر من القائمة للبدء.",
        reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    user_id = msg.from_user.id
    text = (msg.text or "").strip()
    # maintenance check
    if is_active():
        bot.send_message(user_id, "⚠️ البوت تحت الصيانة مؤقتًا. حاول لاحقًا.")
        return

    # MAIN MENU
    if text == "ابدأ البحث":
        bot.send_message(user_id, "اختر نوع الدورات:", reply_markup=search_type_keyboard())
        return

    if text in ["دورات عربية", "دورات أجنبية"]:
        bot.send_message(user_id, "اختر نوع الدورات:", reply_markup=course_kind_keyboard())
        # store lang
        db = SessionLocal()
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            last = u.searched_categories or []
            if not isinstance(last, list):
                last = []
            last.insert(0, {"lang": "ar" if text == "دورات عربية" else "en"})
            u.searched_categories = last[:10]
            db.commit()
        db.close()
        return

    if text in ["مجاني", "مدفوع"]:
        bot.send_message(user_id, "اختر المجال:", reply_markup=categories_keyboard())
        db = SessionLocal()
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            last = u.searched_categories or []
            if not isinstance(last, list):
                last = []
            last.insert(0, {"type": text})
            u.searched_categories = last[:10]
            db.commit()
        db.close()
        return

    # categories
    categories = ["برمجة", "تصميم", "ذكاء اصطناعي", "تسويق", "أمن سيبراني", "لغات", "أعمال", "أخرى"]
    if text in categories:
        # store category and ask topic
        db = SessionLocal()
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            last = u.searched_categories or []
            if not isinstance(last, list):
                last = []
            last.insert(0, {"category": text})
            u.searched_categories = last[:10]
            db.commit()
        db.close()
        bot.send_message(user_id, "أكتب الموضوع الذي تريده (مثال: تعلم بايثون):", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add("رجوع"))
        return

    if text == "رجوع":
        bot.send_message(user_id, "تم الرجوع.", reply_markup=main_keyboard())
        return

    # detect topic input (if user has a category stored)
    db = SessionLocal()
    u = db.query(User).filter(User.id == user_id).first()
    search_ctx = None
    if u:
        last = u.searched_categories or []
        if isinstance(last, list):
            # find last category entry
            for item in last:
                if isinstance(item, dict) and "category" in item:
                    search_ctx = {"category": item.get("category")}
                    break
            # get lang/type
            if last and isinstance(last[0], dict):
                if "lang" in last[0]:
                    search_ctx["lang"] = last[0]["lang"]
                if "type" in last[0]:
                    search_ctx["type"] = last[0]["type"]
    db.close()

    if search_ctx and text and text != "إلغاء":
        # treat this as topic
        topic = text
        TEMP[user_id] = {"topic": topic, "ctx": search_ctx}
        bot.send_message(user_id,
            f"🔎 للاستمرار في عملية البحث سيتم خصم {10} نقاط من حسابك.\nهل تريد المتابعة؟",
            reply_markup=confirm_search_keyboard())
        return

    if text == "موافق":
        sess = TEMP.get(user_id)
        if not sess:
            bot.send_message(user_id, "لا توجد عملية بحث معلقة.", reply_markup=main_keyboard())
            return
        # check points
        pts = get_points(user_id)
        if pts < 10:
            bot.send_message(user_id, "رصيدك غير كافٍ. شحن النقاط أو ادعُ أصدقاء للحصول على نقاط.", reply_markup=main_keyboard())
            TEMP.pop(user_id, None)
            return
        # deduct
        ok = deduct_points(user_id, 10, reason="search")
        if not ok:
            bot.send_message(user_id, "تعذر خصم النقاط.", reply_markup=main_keyboard())
            TEMP.pop(user_id, None)
            return
        # perform search
        ctx = sess["ctx"]
        topic = sess["topic"]
        lang = ctx.get("lang", "ar")
        cat = ctx.get("category", "")
        query = f"{topic} {cat}"
        try:
            results = search_courses(query, num_results=10, language=("en" if lang == "en" else "ar"))
        except Exception as e:
            logger.exception("Search failed: %s", e)
            # refund
            add_points(user_id, 10, reason="refund_search_error")
            notify_admin(f"Search error: {e}")
            bot.send_message(user_id, "عذراً حدث خطأ أثناء البحث. تمت استعادة نقاطك.", reply_markup=main_keyboard())
            TEMP.pop(user_id, None)
            return
        # show results
        for i, r in enumerate(results, start=1):
            title = r.get("title")
            link = r.get("link")
            snippet = r.get("snippet") or ""
            rating = r.get("rating") or "غير متوفر"
            desc = (snippet[:77] + "...") if len(snippet) > 80 else snippet
            msg = f"📘 {i}. {title}\n⭐ التقييم: {rating}\n📄 الوصف: {desc}\n🔗 {link}"
            # show with option to add to favorites (ReplyKeyboard)
            bot.send_message(user_id, msg, reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add("إضافة للمفضلة"))
        bot.send_message(user_id, "انتهت النتائج.", reply_markup=main_keyboard())
        TEMP.pop(user_id, None)
        return

    if text == "لا":
        TEMP.pop(user_id, None)
        bot.send_message(user_id, "تم إلغاء البحث.", reply_markup=main_keyboard())
        return

    # Points packages
    if text in ["100 نقطة – 0.5 TON", "250 نقطة – 1 TON", "500 نقطة – 2 TON"]:
        mapping = {"100 نقطة – 0.5 TON": ("100", 0.5), "250 نقطة – 1 TON": ("250", 1), "500 نقطة – 2 TON": ("500", 2)}
        key, ton = mapping[text]
        bot.send_message(user_id, f"حسناً. يرجى تحويل {ton} TON إلى المحفظة التالية:\n\n{os.getenv('TON_WALLET_ADDRESS')}\n\nبعد التحويل اضغط 'لقد قمت بالدفع'.", reply_markup=payment_confirm_keyboard())
        # create pending record in DB (omitted short) - admin will confirm manually
        return

    if text == "لقد قمت بالدفع":
        notify_admin(f"طلب شحن نقاط من @{msg.from_user.username or user_id}")
        bot.send_message(user_id, "شكراً، تم استلام طلب الشحن وسيتم التحقق منه.", reply_markup=main_keyboard())
        return

    if text == "المفضلات":
        favs = get_favorites(user_id)
        if not favs:
            bot.send_message(user_id, "ليس لديك أي مفضلات حالياً.", reply_markup=main_keyboard())
            return
        for f in favs:
            bot.send_message(user_id, f"⭐ {f.get('title')}\n🔗 {f.get('link')}", reply_markup=main_keyboard())
        return

    if text == "إضافة للمفضلة":
        # simplified: add last search result stored in TEMP (not robust but works per single session)
        last = TEMP.get(user_id, {}).get("last_result")
        if not last:
            bot.send_message(user_id, "لا توجد نتيجة لحفظها.", reply_markup=main_keyboard())
            return
        success = add_favorite(user_id, last)
        if success:
            bot.send_message(user_id, "تمت الإضافة إلى المفضلات.", reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "موجودة بالفعل في المفضلات.", reply_markup=main_keyboard())
        return

    if text == "حسابي":
        pts = get_points(user_id)
        db = SessionLocal()
        u = db.query(User).filter(User.id == user_id).first()
        invited = u.invited_count if u else 0
        is_vip = "VIP" if (u and u.is_vip) else "FREE"
        cats = u.searched_categories if u else []
        db.close()
        bot.send_message(user_id, f"👤 @{msg.from_user.username or ''}\n💰 النقاط: {pts}\n👥 الدعوات: {invited}\n📂 المجالات الأخيرة: {cats}\n🔖 الحالة: {is_vip}", reply_markup=main_keyboard())
        return

    if text == "رفع دورة":
        pts = get_points(user_id)
        if pts < 100:
            bot.send_message(user_id, "تحتاج 100 نقطة لرفع دورة.", reply_markup=main_keyboard())
            return
        TEMP[user_id] = {"upload_step": "confirm"}
        bot.send_message(user_id, "🔼 رفع دورة يتطلب خصم 100 نقطة. هل تريد المتابعة؟", reply_markup=confirm_upload_keyboard())
        return

    if text == "موافق" and TEMP.get(user_id, {}).get("upload_step") == "confirm":
        ok = deduct_points(user_id, 100, reason="upload_course")
        if not ok:
            bot.send_message(user_id, "تعذر خصم النقاط.", reply_markup=main_keyboard())
            TEMP.pop(user_id, None)
            return
        TEMP[user_id] = {"upload_step": "title"}
        bot.send_message(user_id, "أرسل اسم الدورة الآن:", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add("إلغاء"))
        return

    # collect upload steps
    if TEMP.get(user_id, {}).get("upload_step") == "title":
        TEMP[user_id]["title"] = text
        TEMP[user_id]["upload_step"] = "description"
        bot.send_message(user_id, "أرسل وصف الدورة:", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add("إلغاء"))
        return
    if TEMP.get(user_id, {}).get("upload_step") == "description":
        TEMP[user_id]["description"] = text
        TEMP[user_id]["upload_step"] = "url"
        bot.send_message(user_id, "أرسل رابط الدورة:", reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add("إلغاء"))
        return
    if TEMP.get(user_id, {}).get("upload_step") == "url":
        TEMP[user_id]["url"] = text
        up = create_upload(user_id, TEMP[user_id]["title"], TEMP[user_id]["description"], TEMP[user_id]["url"])
        notify_admin(f"طلب رفع دورة جديد من @{msg.from_user.username or user_id}:\n{up.title}\n{up.url}")
        bot.send_message(user_id, "تم إرسال طلب رفع الدورة، سيتم مراجعته من الأدمن.", reply_markup=main_keyboard())
        TEMP.pop(user_id, None)
        return

    # admin panel (access)
    if str(user_id) == str(ADMIN_ID) and text == "لوحة الأدمن":
        bot.send_message(user_id, "أهلاً بالأدمن", reply_markup=admin_keyboard())
        return

    # fallback
    bot.send_message(user_id, "آسف لم أفهم. اختر من الأزرار أو اضغط /start.", reply_markup=main_keyboard())

# TEMP memory
TEMP = {}

if __name__ == "__main__":
    # start uvicorn if running directly (Render will run via `uvicorn main:app --host 0.0.0.0 --port $PORT`)
    port = int(os.environ.get("PORT", 8000))
    logger.info("Starting uvicorn on port %s", port)
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")