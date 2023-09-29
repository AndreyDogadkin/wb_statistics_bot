from dataclasses import dataclass


@dataclass
class BotMessagesTemplates:
	send_nm_ids_template = (
		'Артикул: {}\n'
		'Категория товара: {}\n'
		'Номер номенклатуры: {}\n\n'
	)
	plus_send_nm_ids_template = (
		'⚠️ Выберите товар для получения статистики за неделю ⤵️'
	)
	set_state_statistics_mess_template = (
		'Введите числовой номер номенклатуры, '
		'для получения статистики.\n'
		'Пример: "147200496"\n'
	)
	send_analytic_detail_mess_template = (
		'<b>Данные на {}:</b>\n'
		'Сумма заказов: {} р.\n'
		'Количество заказов: {}\n'
		'Просмотров карточки: {}\n'
		'Добавлений в корзину: {}\n'
		'Количество выкупов: {}\n'
		'Процент выкупов: {}%\n'
		'Сумма выкупов: {} р.\n'
		'\n'
	)
