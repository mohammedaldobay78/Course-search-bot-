# keyboards.py
from telebot import types

def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("ابدأ البحث")
    kb.add("رفع دورة")
    kb.add("شحن النقاط")
    kb.add("حسابي")
    kb.add("المفضلات")
    kb.add("النشاط اليومي")
    kb.add("دعوة صديق")
    kb.add("الدعم")
    return kb

def search_type_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("دورات عربية", "دورات أجنبية")
    kb.add("رجوع")
    return kb

def course_kind_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("مجاني", "مدفوع")
    kb.add("رجوع")
    return kb

def categories_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    categories = ["برمجة", "تصميم", "ذكاء اصطناعي", "تسويق", "أمن سيبراني", "لغات", "أعمال", "أخرى"]
    for c in categories:
        kb.add(c)
    kb.add("رجوع")
    return kb

def confirm_search_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("موافق", "لا")
    kb.add("رجوع")
    return kb

def confirm_upload_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("موافق", "إلغاء")
    return kb

def points_packages_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("100 نقطة – 0.5 TON", "250 نقطة – 1 TON", "500 نقطة – 2 TON")
    kb.add("رجوع")
    return kb

def payment_confirm_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("لقد قمت بالدفع", "رجوع")
    return kb

def admin_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    kb.add("عرض المستخدمين", "طلبات الشحن")
    kb.add("طلبات رفع الدورات", "إرسال إشعار")
    kb.add("الإحصائيات", "تشغيل/إيقاف البحث")
    kb.add("قائمة الحظر", "رجوع")
    return kb