err_mess_templates: dict = {
    'try_later': 'При выполнении запроса произошла непредвиденная ошибка.\n'
                 'Мы уже занимаемся ее устранением, повторите попытку позже.\n'
                 '🤕',

    'incorrect_token': '🚫 Некорректный API ключ, проверьте вводимые данные и повторите попытку.\n\n'
                       'Для получения инструкции /help\n'
                       'Для отмены ввода токена нажмите ❌ ниже.',

    'error_401': '🚫 Ошибка доступа.\n'
                 'Возможно, вы ввели ключ не того типа, либо он уже отозван.\n'
                 'Если ваш токен ранее был сохранен, пожалуйста обновите его командой /token.\n\n'
                 'Для получения инструкции /help\n',

    'no_data': ' 😶 Нет данных для по выбранной номенклатуре за выбранный период.',

    'no_active_nms': '📭 Активных номеров номенклатур не найдено.',
    'error_try_later_sticker': 'CAACAgIAAxkBAAEBjxVlNENylv6-XrO94jUBR82Sisq-XAACYwAD29t-AAGMnQU950KD5zAE',
    'error_401_sticker': 'CAACAgIAAxkBAAEBjx9lNEXeF9goYdFPj6v_195o3fkZRgACXwAD29t-AAGEsFSbEa7K4zAE'
}

info_mess_templates: dict = {
    'start': 'Привет, {}.\n'
             'Я бот WB Statistics v0.5 👋\n'
             'Я помогу тебе быстро получать информацию о твоих продажах на Wildberries 🫐\n\n'
             '💡 Для получения инструкции /help.',
    'help': '''
<b>Инструкция по использованию WB Statistics Bot.</b>

Бот работает в формате запросов к WB API, поэтому для получения статистики, необходимо получить API ключ в личном кабинете WB Partners.

✱ <b>Как получить WB API ключ:</b>
1. Создайте API ключ в разделе Профиль --> Настройки --> Доступ к API.
2. Сохраните данный ключ.

✱ <b>Как пользоваться ботом:</b>
1. Нажмите кнопку Menu и выберите подходящую команду.
2. Введите сохраненный API ключ. Ваш ключ автоматически удаляется из диалога после каждого запроса.
3. Следуйте инструкциям полученным из сообщений бота.
 
✱ <b>Команды:</b>
✦ <i>/get_stats</i> ✦:
✧ <i>Позволяет получить статистику по одному выбранному артикулу за выбранный период.
Статистика, полученная за периоды от 1 до 5 дней, отображается в формате дней.
Статистика от недели до 6 месяцев отображается в формате выбранного периода и предыдущего периода равного выбранному.
</i>
✧ <u>Как пользоваться</u>:
1. Если ваш API ключ не был сохранен ранее, введите его по запросу бота.
2. Выберите артикул по которому Вы хотите получить статистику.
3. Выберите из предложенных вариантов период для получения статистики.
4. Статистика получена.
 
✦ <i>/token</i> ✦:
<i>Позволяет сохранить API ключи видов "Стандартный" и "Статистика".
Сохранение ключей позволяет упростить и ускорить процесс получения статистики.
Без сохранения ключ необходимо будет присылать для каждого нового запроса.
API ключи хранятся в нашей базе в зашифрованном виде, тем не менее, рекомендуется обновлять их, хотя бы, раз в 2 недели.
</i>
✧ <u>Как пользоваться</u>:
1. ...
2. ...
    '''
}

get_stats_mess_templates: dict = {
    'send_token_standard': '🔑 Для выполнения операции отправьте '
                           'токен WB API "Стандартный".',
    'change_nm_id': '📑 В сообщении представлены ваши номенклатуры.\n'
                    'Выберите нужный артикул и нажмите соответсвующую кнопку на клавиатуре под ниже.\n\n',
    'send_nm_ids_template':
        '❇️  Артикул: <u>{}</u>\n'
        '🗂️  Категория: {}\n'
        '🆔  Номер номенклатуры: {}\n'
        '_________\n\n',

    'plus_send_nm_ids_template': '💡 Для получения статистики выберите нужный артикул ⤵️',

    'set_state_statistics_mess_template':
        'Введите числовой номер номенклатуры, '
        'для получения статистики.\n'
        'Пример: "147200496"\n',

    'set_get_period_state': '📆 Выберите период для получения статистики.\n\n'
                            '💡 От 1 до 5 дней статистика будет разделена по дням, '
                            'от недели и более сгруппирована по выбранному периоду, '
                            'плюс за предыдущий период равный выбранному.',

    'send_analytic_detail_days_mess_template':
        ' <i><b>✦ <u>Данные за {} </u>✦</b>\n'
        '💸  Сумма заказов: <u>{} р.</u>\n'
        '🚚  Количество заказов: <u>{} шт.</u>\n'
        '👀  Просмотров карточки: {}\n'
        '🛒  Добавлений в корзину: {}\n'
        '💯  Количество выкупов: {}\n'
        '🤑  Сумма выкупов: {} р.\n'
        '🛍️  Процент выкупов: {} %</i>\n'
        '📈  К-сия добавлений в корзину: {} %\n'
        '📊  К-сия выкупов из корзины: {} %\n'
        '\n',

    'send_analytic_detail_period_mess_template':
        '<b> ✦ <u>{}</u>\n'
        ' ✦ <u>{} - {} </u></b>\n'
        '💸  Сумма заказов: {} р.\n'
        '🚚  Количество заказов: {}\n'
        '👀  Просмотров карточки: {}\n'
        '🛒  Добавлений в корзину: {}\n'
        '💯  Количество выкупов: {}\n'
        '🤑  Сумма выкупов: {} р.\n'
        '🙅  Кол-во возвратов: {}\n'
        '🪃  Сумма возвратов: {} р.\n'
        '📈  Среднее кол-во заказов в день: {}\n'
        '📊  Средняя цена заказа: {}\n'
        '🛍️  Процент выкупов: {} %\n'
        '\n',
}

save_token_mess_templates: dict = {
    'change_token_type': '‼️ Выберите тип сохраняемого/обновляемого токена.\n\n'
                         '💡 На данный момент весь функционал доступен с типом токена "Стандартный".',
    'input_standard_token': '🤫 Введите токен типа "Стандартный".',
    'token_updated': '🔑 Токен сохранен!\n'
                     'Для проверки выполните команду /get_stats 👌'
}
