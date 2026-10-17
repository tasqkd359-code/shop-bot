import os
import json
import discord
from discord.ext import commands

# إعداد الصلاحيات
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

DB_FILE = 'shop_db.json'

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "products": {}}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "products": {}}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول بنجاح باسم: {bot.user}')

# --- أمر قائمة الأوامر ---
@bot.command(name="اوامر", aliases=["الاوامر", "help"])
async def show_help(ctx):
    embed = discord.Embed(
        title="🛒 قائمة أوامر بوت الشوب",
        description="إليك جميع الأوامر المتاحة لاستخدام البوت:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="👑 أوامر الإدارة",
        value=(
            "`!اضافة_منتج <الكود> \"<الاسم>\" <السعر>` - إضافة منتج جديد للمتجر\n"
            "`!تعبئة_مخزون <كود المنتج> <الكود1> <الكود2> ...` - إضافة أكواد للمخزون\n"
            "`!اضافة_رصيد @العضو <المبلغ>` - شحن رصيد لعضو معين"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛒 أوامر الأعضاء",
        value=(
            "`!المتجر` - عرض جميع المنتجات والأسعار والمخزون\n"
            "`!رصيدي` - معرفة رصيدك الحالي في المتجر\n"
            "`!شراء <كود المنتج>` - شراء منتج واستلام الكود في الخاص"
        ),
        inline=False
    )
    
    embed.set_footer(text="نتمنى لك تجربة تسوق ممتعة!")
    await ctx.send(embed=embed)

# --- أوامر المتجر ---
@bot.command(name="اضافة_منتج")
@commands.has_permissions(administrator=True)
async def add_product(ctx, code: str, name: str, price: float):
    db = load_db()
    db["products"][code] = {"name": name, "price": price, "stock": []}
    save_db(db)
    await ctx.send(f"✅ تم إضافة المنتج **{name}** (الكود: `{code}`) بسعر **{price}** بنجاح!")

@bot.command(name="تعبئة_مخزون")
@commands.has_permissions(administrator=True)
async def restock(ctx, code: str, *items: str):
    db = load_db()
    if code not in db["products"]:
        await ctx.send("❌ هذا المنتج غير موجود!")
        return
    db["products"][code]["stock"].extend(items)
    save_db(db)
    await ctx.send(f"📦 تم إضافة {len(items)} عنصر/كود إلى مخزون **{db['products'][code]['name']}**.")

@bot.command(name="اضافة_رصيد")
@commands.has_permissions(administrator=True)
async def add_balance(ctx, member: discord.Member, amount: float):
    db = load_db()
    user_id = str(member.id)
    db["users"][user_id] = db["users"].get(user_id, 0) + amount
    save_db(db)
    await ctx.send(f"💰 تم إضافة **{amount}** إلى رصيد {member.mention}. الرصيد الحالي: **{db['users'][user_id]}**")

@bot.command(name="المتجر")
async def show_shop(ctx):
    db = load_db()
    products = db.get("products", {})
    if not products:
        await ctx.send("🛒 المتجر فارغ حالياً!")
        return
    
    embed = discord.Embed(title="🏪 قائمة المنتجات المتاحة", color=discord.Color.green())
    for code, info in products.items():
        stock_count = len(info.get("stock", []))
        embed.add_field(
            name=f"{info['name']} (كود: `{code}`)",
            value=f"💵 السعر: **{info['price']}** | 📦 المتوفر: **{stock_count}**",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name="رصيدي")
async def check_balance(ctx):
    db = load_db()
    user_id = str(ctx.author.id)
    balance = db["users"].get(user_id, 0)
    await ctx.send(f"💳 رصيدك الحالي هو: **{balance}**")

@bot.command(name="شراء")
async def buy(ctx, code: str):
    db = load_db()
    user_id = str(ctx.author.id)
    user_balance = db["users"].get(user_id, 0)
    
    if code not in db["products"]:
        await ctx.send("❌ المنتج غير موجود!")
        return
    
    product = db["products"][code]
    if user_balance < product["price"]:
        await ctx.send(f"❌ رصيدك غير كافٍ! سعر المنتج **{product['price']}** ورصيدك الحالي **{user_balance}**.")
        return
    
    if not product["stock"]:
        await ctx.send("❌ عذراً، هذا المنتج غير متوفر بالمخزون حالياً!")
        return
    
    item = product["stock"].pop(0)
    db["users"][user_id] -= product["price"]
    save_db(db)
    
    try:
        await ctx.author.send(f"🎉 شكراً لشراء **{product['name']}**!\n🎁 الكود الخاص بك هو:\n```{item}```")
        await ctx.send(f"✅ تم الشراء بنجاح! تم إرسال المنتج إلى الخاص بك يا {ctx.author.mention}.")
    except discord.Forbidden:
        await ctx.send(f"⚠️ تم الشراء وخصم المبلغ، ولكن الخاص لديك مغلق! يرجى فتحه ثم التواصل مع الإدارة لاستلام المنتج.")

TOKEN = os.getenv('TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("خطأ: لم يتم العثور على متغير البيئة TOKEN!")
