import discord
from discord.ext import commands
import json
import os

# إعدادات البوت والبادئة
PREFIX = "!"
TOKEN = os.getenv("TOKEN")  # إذا كنت تستخدم متغيرات البيئة في ريلواي، أو استبدله بالتوكن مباشرة بين علامتي تنصيص

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

DB_FILE = "shop_db.json"

# --- دوال التعامل مع قاعدة البيانات ---

def load_data():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "products": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_balance(user_id):
    data = load_data()
    return data["users"].get(str(user_id), 0)

def add_balance(user_id, amount):
    data = load_data()
    uid = str(user_id)
    data["users"][uid] = data["users"].get(uid, 0) + amount
    save_data(data)

# --- أحداث البوت ---

@bot.event
async def on_ready():
    print(f"تم تشغيل بوت المتجر بنجاح باسم: {bot.user}")

# --- أوامر الأعضاء ---

@bot.command(name="رصيدي", aliases=["balance"])
async def check_balance(ctx):
    bal = get_balance(ctx.author.id)
    embed = discord.Embed(
        title="💳 رصيدك الحالي",
        description=f"رصيدك هو: **{bal}** نقطة/ريال",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command(name="المتجر", aliases=["shop"])
async def show_shop(ctx):
    data = load_data()
    products = data.get("products", {})

    if not products:
        return await ctx.send("المتجر فارغ حالياً.")

    embed = discord.Embed(title="🛒 المتجر الإلكتروني", color=discord.Color.green())

    for key, item in products.items():
        stock_count = len(item.get("stock", []))
        embed.add_field(
            name=f"📦 {item['name']} (كود المنتج: `{key}`)",
            value=f"السعر: **{item['price']}** | المتوفر: **{stock_count}**",
            inline=False
        )

    embed.set_footer(text="للشراء اكتب: !شراء <كود_المنتج>")
    await ctx.send(embed=embed)

@bot.command(name="شراء", aliases=["buy"])
async def buy_product(ctx, item_key: str):
    data = load_data()
    products = data.get("products", {})

    if item_key not in products:
        return await ctx.send("❌ هذا المنتج غير موجود.")

    product = products[item_key]
    price = product["price"]
    stock = product.get("stock", [])

    if len(stock) == 0:
        return await ctx.send("❌ هذا المنتج غير متوفر حالياً (خارج المخزون).")

    user_bal = get_balance(ctx.author.id)
    if user_bal < price:
        return await ctx.send(f"❌ رصيدك غير كافي. يحتاج المنتج **{price}** ورصيدك هو **{user_bal}**.")

    # خصم الرصيد وسحب كود من المخزون
    add_balance(ctx.author.id, -price)
    item_code = stock.pop(0)
    data["products"][item_key]["stock"] = stock
    save_data(data)

    # إرسال المنتج في الخاص
    try:
        dm_embed = discord.Embed(
            title="🎉 تم الشراء بنجاح!",
            description=f"المنتج: **{product['name']}**\nالكود الخاص بك:\n```{item_code}```",
            color=discord.Color.gold()
        )
        await ctx.author.send(embed=dm_embed)
        await ctx.send(f"✅ تم الشراء بنجاح يا {ctx.author.mention}! أرسلنا لك المنتج في الخاص.")
    except discord.Forbidden:
        await ctx.send(f"⚠️ {ctx.author.mention} تم الشراء وخصم الرصيد، لكن الخاص لديك مغلق! افتح الخاص للتواصل معنا.")

# --- أوامر الإدارة ---

@bot.command(name="اضافة_رصيد")
@commands.has_permissions(administrator=True)
async def admin_add_bal(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        return await ctx.send("المبلغ يجب أن يكون أكبر من 0.")
    add_balance(member.id, amount)
    await ctx.send(f"✅ تم إضافة **{amount}** إلى رصيد {member.mention}.")

@bot.command(name="اضافة_منتج")
@commands.has_permissions(administrator=True)
async def admin_add_product(ctx, item_key: str, name: str, price: int):
    data = load_data()
    if item_key in data["products"]:
        return await ctx.send("هذا الكود موجود مسبقاً لمنتج آخر.")

    data["products"][item_key] = {
        "name": name,
        "price": price,
        "stock": []
    }
    save_data(data)
    await ctx.send(f"✅ تم إضافة المنتج **{name}** بسعر **{price}**.")

@bot.command(name="تعبئة_مخزون")
@commands.has_permissions(administrator=True)
async def admin_add_stock(ctx, item_key: str, *, codes: str):
    code_list = codes.split()
    data = load_data()

    if item_key not in data["products"]:
        return await ctx.send("المنتج غير موجود.")

    data["products"][item_key]["stock"].extend(code_list)
    save_data(data)
    await ctx.send(f"✅ تم إضافة **{len(code_list)}** كود إلى مخزون **{data['products'][item_key]['name']}**.")

# تشغيل البوت (تأكد من وضع التوكن هنا أو عبر متغيرات البيئة في ريلواي)
bot.run(TOKEN)
