import os
import csv
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters, ConversationHandler
from fpdf import FPDF

BOT_TOKEN = os.environ.get("8772713813:AAFcNvQL63gNZKtvyJjj_WqgtmJLSWZ2zc8")

# ---------------- BASIC COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! I'm your practice bot. Send me anything and I'll echo it back.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start - welcome message\n/help - this menu")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END
# redeploy trigger
# ---------------- INVOICE CONVERSATION ----------------

CUSTOMER, SERVICE, AMOUNT = range(3)

async def invoice_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's create an invoice.\n\nCustomer name?")
    return CUSTOMER

async def get_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["customer"] = update.message.text
    await update.message.reply_text("Service?")
    return SERVICE

async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Amount?")
    return AMOUNT

def save_invoice(invoice_number, date, customer, service, amount):
    file_exists = os.path.exists("invoices.csv")
    with open("invoices.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Invoice #", "Date", "Customer", "Service", "Amount"])
        writer.writerow([invoice_number, date, customer, service, amount])

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["amount"] = update.message.text
    data = context.user_data

    invoice_number = f"INV-{datetime.date.today().year}-{update.effective_user.id % 1000:03d}"
    today = datetime.date.today().strftime("%b %d, %Y")
    save_invoice(invoice_number, today, data["customer"], data["service"], data["amount"])

    business_name = "GoFar Tour And Travel"
    business_tagline = "Save YOUR Time And Money"
    business_phone = "+251-9X34-376578"
    business_email = "GoFar12u@example.com"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    if os.path.exists("logo.png.png"):
        pdf.image("logo.png.png", x=10, y=8, w=25)

    GREEN = (20, 110, 75)
    GRAY = (110, 110, 110)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*GREEN)
    pdf.set_xy(38, 14)
    pdf.cell(90, 10, business_name, align="L", ln=False)

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 30, 30)
    pdf.set_xy(130, 10)
    pdf.cell(70, 10, "INVOICE", align="R", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.set_xy(38, 22)
    pdf.cell(90, 6, business_tagline, align="L", ln=False)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(130, 20)
    pdf.cell(70, 6, f"Date: {today}", align="R", ln=True)
    pdf.set_xy(130, 26)
    pdf.cell(70, 6, f"Invoice #: {invoice_number}", align="R", ln=True)

    pdf.set_draw_color(*GREEN)
    pdf.set_line_width(1)
    pdf.line(10, 35, 200, 35)

    pdf.set_xy(10, 42)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(90, 5, "PREPARED FOR", ln=False)
    pdf.set_xy(110, 42)
    pdf.cell(90, 5, "PREPARED BY", align="R", ln=True)

    pdf.set_xy(10, 48)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(90, 6, data["customer"], ln=False)
    pdf.set_xy(110, 48)
    pdf.cell(90, 6, business_name, align="R", ln=True)

    pdf.set_xy(110, 54)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(90, 5, business_phone, align="R", ln=True)
    pdf.set_xy(110, 59)
    pdf.cell(90, 5, business_email, align="R", ln=True)

    pdf.set_xy(10, 75)
    pdf.set_fill_color(*GREEN)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(140, 10, "  Description", border=0, fill=True)
    pdf.cell(50, 10, "Amount  ", border=0, fill=True, align="R", ln=True)

    pdf.set_x(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(140, 10, "  " + data["service"], border="B")
    pdf.cell(50, 10, f"{data['amount']} ETB  ", border="B", align="R", ln=True)

    pdf.set_xy(110, 100)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(45, 7, "Total", ln=False)
    pdf.cell(45, 7, f"{data['amount']} ETB", align="R", ln=True)

    pdf.set_xy(110, 107)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*GREEN)
    pdf.cell(45, 8, "Balance Due", ln=False)
    pdf.cell(45, 8, f"{data['amount']} ETB", align="R", ln=True)

    pdf.set_xy(10, 280)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, f"{business_name} · {business_email}    Thank you for your business!", ln=True)

    filename = f"invoice_{update.effective_user.id}.pdf"
    pdf.output(filename)

    await update.message.reply_document(document=open(filename, "rb"), filename="invoice.pdf")
    os.remove(filename)

    return ConversationHandler.END

invoice_handler = ConversationHandler(
    entry_points=[CommandHandler("invoice", invoice_start)],
    states={
        CUSTOMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_customer)],
        SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
        AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

# ---------------- REPORT ----------------

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("invoices.csv"):
        await update.message.reply_text("No invoices yet.")
        return

    total = 0
    count = 0
    with open("invoices.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                total += float(row["Amount"].replace(",", ""))
                count += 1
            except ValueError:
                pass

    await update.message.reply_text(
        f"📊 Report\n\nTotal invoices: {count}\nTotal amount: {total:,.0f} ETB"
    )

# ---------------- CUSTOMER MANAGEMENT ----------------

CUST_NAME, CUST_PHONE, CUST_EMAIL, CUST_ADDRESS = range(3, 7)

def save_customer(name, phone, email, address):
    file_exists = os.path.exists("customers.csv")
    with open("customers.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Phone", "Email", "Address"])
        writer.writerow([name, phone, email, address])

async def addcustomer_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Let's add a customer.\n\nCustomer name?")
    return CUST_NAME

async def get_cust_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cust_name"] = update.message.text
    await update.message.reply_text("Phone number?")
    return CUST_PHONE