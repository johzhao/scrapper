import xlwt

from model.shop_info import ShopInfo
from model.shop_review import ShopReview


def export_shops_to_excel(filepath: str):
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('shops')
    _export_shop_title(sheet)

    shop_infos = ShopInfo.objects().all()
    for row, shop_info in enumerate(shop_infos, 1):
        _export_shop_record(sheet, row, shop_info)

    wbk.save(filepath)


def export_reviews_to_excel(filepath: str):
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('reviews')
    _export_review_title(sheet)

    shop_reviews = ShopReview.objects().all()
    for row, shop_review in enumerate(shop_reviews, 1):
        _export_review_record(sheet, row, shop_review)

    wbk.save(filepath)


def _export_shop_title(sheet: xlwt.Worksheet):
    sheet.write(0, 0, '商户ID')
    sheet.write(0, 1, '商户')
    sheet.write(0, 2, '商户星级')
    sheet.write(0, 3, '评论数量')
    sheet.write(0, 4, '人均消费')
    sheet.write(0, 5, '产品得分')
    sheet.write(0, 6, '环境得分')
    sheet.write(0, 7, '服务得分')
    sheet.write(0, 8, '地址')
    sheet.write(0, 9, '电话')
    sheet.write(0, 10, 'URL')


def _export_shop_record(sheet: xlwt.Worksheet, row: int, shop_info: ShopInfo):
    col = 0
    col = _write_data(sheet, row, col, shop_info.id)
    col = _write_data(sheet, row, col, shop_info.name)
    col = _write_data(sheet, row, col, shop_info.rating)
    col = _write_data(sheet, row, col, shop_info.reviews)
    col = _write_data(sheet, row, col, shop_info.avg_cost)
    col = _write_data(sheet, row, col, shop_info.production_rating)
    col = _write_data(sheet, row, col, shop_info.environment_rating)
    col = _write_data(sheet, row, col, shop_info.service_rating)
    col = _write_data(sheet, row, col, shop_info.address)
    col = _write_data(sheet, row, col, shop_info.phone_number)
    _write_data(sheet, row, col, shop_info.url)


def _export_review_title(sheet: xlwt.Worksheet):
    sheet.write(0, 0, '用户昵称')
    sheet.write(0, 1, '商户ID')
    sheet.write(0, 2, '商户名称')
    sheet.write(0, 3, '星级评价')
    sheet.write(0, 4, '评论文本')
    sheet.write(0, 5, '评论时间')


def _export_review_record(sheet: xlwt.Worksheet, row: int, shop_revieww: ShopReview):
    col = 0
    col = _write_data(sheet, row, col, shop_revieww.username)
    col = _write_data(sheet, row, col, shop_revieww.shop_id)
    col = _write_data(sheet, row, col, shop_revieww.shop_name)
    col = _write_data(sheet, row, col, shop_revieww.rating)
    col = _write_data(sheet, row, col, shop_revieww.comment)
    _write_data(sheet, row, col, shop_revieww.timestamp)


def _write_data(sheet: xlwt.Worksheet, row: int, col: int, data) -> int:
    if data is not None:
        sheet.write(row, col, data)
    return col + 1
