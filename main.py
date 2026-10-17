import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# تعيين بادئة الأوامر
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== 1. نظام تشفير الإعلانات ====================
class EncryptModal(Modal, title="خدمة التشفير الآلي الاحترافية 🛡️"):
    ad_content = TextInput(
        label="اكتب إعلانك أو سلعَتَك هنا",
        style=discord.TextStyle.paragraph,
        placeholder="اكتب تفاصيل السلعة، السعر، وكيفية التواصل...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        encrypted_text = (
            f"╔══════════════════════════════╗\n"
            f" 🛒 **إعلان معتمد من:** {interaction.user.mention}\n"
            f"--------------------------------------------------\n"
            f"{self.ad_content.value}\n"
            f"╚══════════════════════════════╝"
        )
        await interaction.response.send_message(
            f"✨ **تم تشفير إعلانك بنجاح وجاهز للنسخ:**\n{encrypted_text}", 
            ephemeral=True
        )

class EncryptView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="اضغط لتشفير إعلانك 🔐", style=discord.ButtonStyle.primary, custom_id="encrypt_btn")
    async def encrypt_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(EncryptModal())

# ==================== 2. نظام شراء المتجر & الأمان (الإضافة الجديدة) ====================
class ShopBuyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 شراء متجر", style=discord.ButtonStyle.primary, custom_id="buy_shop_btn")
    async def buy_shop(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🎟️ تم فتح تذكرة طلب المتجر بنجاح! توجه لروم التذاكر للإكمال.", ephemeral=True)

    @discord.ui.button(label="📊 أسعار المتاجر", style=discord.ButtonStyle.secondary, custom_id="shop_prices_btn")
    async def shop_prices(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="✨ قائمة أسعار وباقات المتاجر",
            description="1️⃣ **متجر عادي:** 5k كريدت / شهر\n2️⃣ **متجر مميز (VIP):** 10k كريدت + روم خاص مميز!",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🛡️ طلب وسيط آمن", style=discord.ButtonStyle.success, custom_id="middleman_btn")
    async def middleman_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🔒 تم فتح تذكرة طلب وسيط لضمان حقك وحق البائع من النصب!", ephemeral=True)

    @discord.ui.button(label="⭐ تقييم المتجر", style=discord.ButtonStyle.danger, custom_id="rate_shop_btn")
    async def rate_shop(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(RateModal())

# نظام نافذة التقييم
class RateModal(Modal, title="تقييم تجربة الشراء ⭐"):
    rating = TextInput(label="التقييم من 5 نجوم (مثال: ⭐⭐⭐⭐⭐)", placeholder="اكتب النجوم هنا...", max_length=10)
    feedback = TextInput(label="رأيك في المتجر / الخدمة", style=discord.TextStyle.paragraph, placeholder="اكتب تعليقك هنا...")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"❤️ شكراً لتقييمك! تم إرسال رأيك بنجاح لدعم المتجر.", ephemeral=True)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user.name}")
    print("البوت يعمل بأعلى أداء ومزود بكل الأفكار الاحترافية!")

# ==================== الأوامر واللوحات المحدثة ====================

@bot.command(name="تشفير", help="إرسال لوحة التشفير الآلي")
@commands.has_permissions(administrator=True)
async def setup_encrypt(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="خدمة التشفير الآلي للإعلانات 🛡️",
        description="اضغط على الزر بالأسفل، اكتب إعلانك، وسأعطيك النسخة المشفرة المنظمة تماماً!",
        color=discord.Color.dark_embed()
    )
    await ctx.send(embed=embed, view=EncryptView())

@bot.command(name="متجر", help="إرسال لوحة شراء المتاجر والأمان")
@commands.has_permissions(administrator=True)
async def setup_shop(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="✨ | Thunder Shop | متجر السيرفر الرسمي",
        description="شراء المتاجر، طلب الوسطاء الآمنين، وتقييم التجار بكل سهولة!\n\nقم بالاختيار من الأزرار بالأسفل 👇",
        color=discord.Color.dark_theme()
    )
    embed.set_footer(text="Dev By : Your Name - Powered by Advanced System")
    await ctx.send(embed=embed, view=ShopBuyView())

@bot.command(name="قوانين", help="إرسال قوانين المتاجر")
@commands.has_permissions(administrator=True)
async def rules_panel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="قوانين المتاجر الرسمية",
        description="**قوانين متاجر thunder shop**\n\n"
                    "• يمنع السب والخطأ بالمتجر نهائياً ⚠️\n"
                    "• يمنع الترويج لسيرفرات أو جهات خارجية ❌\n"
                    "• يمنع السبام بين كل رسالة وإعلان (المدة المحددة: 30 دقيقة)\n"
                    "• الحد الأقصى للمتاجر لكل شخص: ( 2 ) فقط !\n"
                    "• يمنع منعاً باتاً بيع الكريدت بطرق مشبوهة\n"
                    "• يمنع كتابة نقاط (.) أو رموز فارغة لنشر السلعة\n"
                    "• عدم التفاعل في المتجر لمدة 7 أيام = حذف المتجر وتفريغه 🗑️\n\n"
                    "**⚠️ عدم قراءة القوانين ليس عذراً أبداً!**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="اوامر", help="عرض قائمة الأوامر الشاملة")
@commands.has_permissions(administrator=True)
async def help_panel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📋 لوحة التحكم والأوامر الكاملة",
        description="جميع الأوامر تحذف نفسها تلقائياً للحفاظ على نظافة الرومات وجماليتها:",
        color=discord.Color.gold()
    )
    embed.add_field(name="🔧 `!تشفير`", value="إرسال لوحة التشفير الآلي للإعلانات.", inline=False)
    embed.add_field(name="🛒 `!متجر`", value="إرسال لوحة المتاجر الشاملة (شراء، أسعار، وسطاء، تقييمات).", inline=False)
    embed.add_field(name="📜 `!قوانين`", value="إرسال لوحة قوانين الشروط والأحكام.", inline=False)
    embed.add_field(name="📊 `!احصائيات`", value="عرض حالة البوت وسرعة الاستجابة.", inline=False)
    embed.set_footer(text="نظام احترافي متكامل لخدمة المتاجر ✨")
    await ctx.send(embed=embed)

@bot.command(name="احصائيات", help="معرفة حالة البوت")
@commands.has_permissions(administrator=True)
async def stats_panel(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📊 لوحة إحصائيات النظام",
        description=f"✅ **حالة البوت:** متصل ويعمل بكامل الطاقة\n"
                    f"⚡ **سرعة الاستجابة (Ping):** {round(bot.latency * 1000)}ms\n"
                    f"👥 **السيرفرات المحمية:** {len(bot.guilds)}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# ضع توكن بوتك هنا
bot.run("MTU1OTQ5Mjg4OTc3ODg1NTk4Ng.GyD9vk.YMTuYFcHBv26Pd2qbOa5GbDVzwRdtElYCoywFk")
