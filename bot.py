import asyncio
import subprocess
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from fixer import auto_fix_code

TOKEN = "8385007008:AAHqAVgSsoFfQggGVs_rzLjlrJS6EKzOsfI"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- BUTTON PANEL ----------------

def main_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛠 Fix Python File", callback_data="fix")],
        [InlineKeyboardButton(text="▶ Run Python File", callback_data="run")],
        [InlineKeyboardButton(text="ℹ Help", callback_data="help")],
    ])


# ---------------- START ----------------

@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer(
        "👋 Welcome!\nSend me any .py file.\nI will fix and run it.",
        reply_markup=main_buttons()
    )


# ---------------- RECEIVE PYTHON FILE ----------------

last_file = {}   # store per-user recent file

@dp.message(F.document)
async def get_python_file(msg: types.Message):
    if not msg.document.file_name.endswith(".py"):
        return await msg.answer("⚠ Only .py files allowed!")

    os.makedirs("uploads", exist_ok=True)
    path = f"uploads/{msg.document.file_name}"

    await bot.download(msg.document, destination=path)
    last_file[msg.from_user.id] = path

    await msg.answer("☑ File saved.\nChoose an option:", reply_markup=main_buttons())


# ---------------- BUTTON HANDLER ----------------

@dp.callback_query()
async def callbacks(cb: types.CallbackQuery):
    uid = cb.from_user.id

    if uid not in last_file:
        return await cb.message.answer("⚠ First send a .py file!")

    path = last_file[uid]

    if cb.data == "fix":
        await fix_file(cb, path)

    elif cb.data == "run":
        await run_file(cb, path)

    elif cb.data == "help":
        await cb.message.answer("📘 Send a Python file and I will fix + run it.")

    await cb.answer()


# ---------------- FIX FILE ----------------

async def fix_file(cb, path):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    fixed = auto_fix_code(code)
    fixed_path = path.replace(".py", "_fixed.py")

    with open(fixed_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    await cb.message.answer_document(
        types.FSInputFile(fixed_path),
        caption="🛠 Fixed file ready!"
    )


# ---------------- RUN FILE ----------------

async def run_file(cb, path):
    try:
        res = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = res.stdout + res.stderr
        if not output.strip():
            output = "⚠ File ran but returned no output"

        await cb.message.answer(f"🖥 Output:\n```\n{output}\n```", parse_mode="Markdown")

    except Exception as e:
        await cb.message.answer(f"❌ Error: {e}")


# ---------------- START BOT ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
