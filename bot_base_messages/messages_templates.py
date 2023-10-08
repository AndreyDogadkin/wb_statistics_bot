from dataclasses import dataclass


@dataclass
class BotMessagesTemplates:
	errors = {
		'try_later': 'Ошибка, повторите запрос позже.',
		'check_correct': 'Ошибка, проверьте правильность введенных данных.'
	}
	send_nm_ids_template = (
		'Артикул: {}\n'
		'Категория товара: {}\n'
		'Номер номенклатуры: {}\n\n'
	)
	plus_send_nm_ids_template = (
		'⚠️ Выберите товар для получения статистики ⤵️'
	)
	set_state_statistics_mess_template = (
		'Введите числовой номер номенклатуры, '
		'для получения статистики.\n'
		'Пример: "147200496"\n'
	)
	send_analytic_detail_days_mess_template = (
		' <b>✦ Данные на {} ✦:</b>\n'
		'• Сумма заказов: {} р.\n'
		'• Количество заказов: {}\n'
		'• Просмотров карточки: {}\n'
		'• Добавлений в корзину: {}\n'
		'• Количество выкупов: {}\n'
		'• Процент выкупов: {}%\n'
		'• Сумма выкупов: {} р.\n'
		'\n'
	)
	send_analytic_detail_period_mess_template = (
		' <b>✦ Данные с {}\n'
		' ✦ по {} ✦:</b>\n'
		'• Сумма заказов: {} р.\n'
		'• Количество заказов: {}\n'
		'• Просмотров карточки: {}\n'
		'• Добавлений в корзину: {}\n'
		'• Количество выкупов: {}\n'
		'• Сумма выкупов: {} р.\n'
		'• Среднее кол-во заказов в день: {}\n'
		'• Средняя цена заказа: {}\n'
		'\n'
	)
