from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

# Get default styles
styles = getSampleStyleSheet()

# Add custom styles
styles.add(ParagraphStyle(
    name='CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    spaceAfter=14,
    fontName='Helvetica-Bold'
))

styles.add(ParagraphStyle(
    name='CustomHeader',
    parent=styles['Normal'],
    fontSize=10,
    textColor=colors.white,
    fontName='Helvetica-Bold'
))

styles.add(ParagraphStyle(
    name='CustomText',
    parent=styles['Normal'],
    fontSize=10,
    fontName='Helvetica'
))

def generate_invoice_pdf(order):
    """Генерация PDF счета на оплату"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    # Заголовок
    elements = [Paragraph('СЧЕТ НА ОПЛАТУ', styles['CustomTitle'])]
    


    # Информация о компании
    company_info = [
        ['ООО "Coffee Shop"', f'№ заказа: {order.id}'],
        ['ИНН 1234567890', f'Дата: {order.created_at.strftime("%d.%m.%Y")}'],
        ['КПП 123456789', f'Время: {order.created_at.strftime("%H:%M")}'],
        ['Адрес: г. Москва, ул. Примерная, д. 1', ''],
        ['Телефон: +7 (999) 123-45-67', '']
    ]
    
    company_table = Table(company_info, colWidths=[doc.width/2.0]*2)
    company_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSerif'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(company_table)
    
    # Информация о покупателе
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('ПОКУПАТЕЛЬ:', styles['Heading3']))
    customer_info = f"""
    {order.get_full_name()}
    Телефон: {order.phone}
    Email: {order.email}
    Адрес: {order.address}
    """
    elements.append(Paragraph(customer_info, styles['CustomText']))
    
    # Таблица с товарами
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('СОСТАВ ЗАКАЗА:', styles['Heading3']))
    
    # Заголовок таблицы
    data = [
        ['№', 'Наименование', 'Кол-во', 'Цена', 'Сумма']
    ]
    
    # Данные о товарах
    for i, item in enumerate(order.items.all(), 1):
        data.append([
            str(i),
            item.product.name,
            str(item.quantity),
            f"{item.price:.2f} ₽",
            f"{item.get_cost():.2f} ₽"
        ])
    
    # Итоговая сумма
    data.append(['', '', '', 'Итого:', f"{order.get_total_cost():.2f} ₽"])
    
    # Создаем таблицу
    table = Table(data, colWidths=[20, '*', 50, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSerif-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSerif'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, -2), 1, colors.lightgrey),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ('TOPPADDING', (0, -1), (-1, -1), 10),
        ('FONTNAME', (0, -1), (-2, -1), 'DejaVuSerif-Bold'),
    ]))
    
    elements.append(table)
    
    # Подпись
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("""
        Счет действителен в течение 3 дней с даты выставления.<br/>
        Оплата производится в рублях по курсу ЦБ РФ на день оплаты.<br/>
        Без НДС.
    """, styles['CustomText']))
    
    # Собираем PDF
    doc.build(elements)
    
    # Получаем содержимое буфера и закрываем его
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def generate_receipt_pdf(order):
    """Генерация PDF чека"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(80*mm, 297*mm),  # Ширина 80мм (кассовый чек), высота A4
        rightMargin=5*mm,
        leftMargin=5*mm,
        topMargin=5*mm,
        bottomMargin=5*mm
    )
    
    elements = []
    
    # Заголовок
    elements.append(Paragraph('КАССОВЫЙ ЧЕК', styles['Heading3']))
    elements.append(Paragraph('ООО "Coffee Shop"', styles['Normal']))
    elements.append(Paragraph('ИНН 1234567890', styles['Normal']))
    elements.append(Paragraph('Кассовый чек №' + str(order.id), styles['Normal']))
    elements.append(Paragraph(f'Дата: {order.created_at.strftime("%d.%m.%Y %H:%M")}', styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Разделительная линия
    elements.append(Paragraph('_' * 40, styles['Normal']))
    
    # Товары
    for item in order.items.all():
        elements.append(Paragraph(item.product.name, styles['Normal']))
        elements.append(Paragraph(
            f"{item.quantity} x {item.price:.2f} = {item.get_cost():.2f} ₽",
            styles['Normal']
        ))
    
    # Разделительная линия
    elements.append(Paragraph('_' * 40, styles['Normal']))
    
    # Итого
    elements.append(Paragraph(f'ИТОГО: {order.get_total_cost():.2f} ₽', styles['Heading3']))
    elements.append(Spacer(1, 5))
    
    # Оплата
    elements.append(Paragraph(f'ОПЛАТА: {order.get_payment_method_display().upper()}', styles['Normal']))
    elements.append(Paragraph('В том числе НДС: Без НДС', styles['Normal']))
    elements.append(Spacer(1, 5))
    
    # Подпись
    elements.append(Paragraph('СПАСИБО ЗА ПОКУПКУ!', styles['Heading3']))
    elements.append(Paragraph('www.coffeeshop.example.com', styles['Normal']))
    
    # Собираем PDF
    doc.build(elements)
    
    # Получаем содержимое буфера и закрываем его
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
