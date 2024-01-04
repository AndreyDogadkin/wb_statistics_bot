err_mess_templates: dict = {
    'try_later': 'При выполнении запроса произошла непредвиденная ошибка.\n'
                 'Мы уже занимаемся ее устранением, повторите попытку позже.\n'
                 '🤕',

    'incorrect_token': '🚫 Некорректный API ключ, проверьте вводимые '
                       'данные и повторите попытку.\n\n'
                       'Для получения инструкции /help\n'
                       'Для отмены ввода токена нажмите ❌ ниже.',

    'error_401': '🚫 Ошибка доступа.\n'
                 'Возможно, вы ввели ключ не того типа, либо он уже отозван.\n'
                 'Если ваш токен ранее был сохранен, пожалуйста обновите '
                 'его командой /token.\n\n'
                 'Для получения инструкции /help\n',
    'error_429': '🚫 Слишком много запросов.\n'
                 'WB API в некоторых случаях не позволяет делать больше 3 '
                 'запросов в минуту. Сделайте небольшую паузу и повторите '
                 'попытку.',

    'response_validation_error': '😰 Неожиданный ответ от WB API, '
                                 'повторите запрос позже.',

    'response_error_field_true': '🧐 В ответе присутствуют ошибки, '
                                 'попробуйте повторить запрос.',

    'timeout_error': '👷 WB API не отвечает, возможно проводятся '
                     'технические работы.',

    'no_data': ' 😶 Нет данных для по выбранной номенклатуре за '
               'выбранный период.',

    'no_active_nms': '📭 Активных номеров номенклатур не найдено.',
    'telegram_error': '💬 У телеграм возникла ошибка во время обработки, '
                      'попробуйте позже.',
}

info_mess_templates: dict = {
    'start': 'Привет, {}.\n'
             'Я бот WB Statistics v0.5 👋\n'
             'Я помогу тебе быстро получать информацию '
             'о твоих продажах на Wildberries 🫐\n\n'
             '💡 Для получения инструкции /help.',

    'cancel': '😉 Состояние сброшено, вы можете использовать все команды.',

    'change_chapter': '📚 Инструкция WB Statistics bot.\n\n'
                      '💡 Выберите раздел инструкции, '
                      'с которым вы хотели бы ознакомиться:',

    'help_token': '🔑 Раздел "API Ключи"\n\n'
                  'Бот работает в формате запросов к WB API, '
                  'поэтому для получения статистики, необходимо получить '
                  'API ключи в личном кабинете WB Partners.\n\n'
                  '✱ <b>Как получить WB API ключи:</b>\n'
                  '1. Создайте API ключи типов "Контент" и "Аналитика" в '
                  'разделе Профиль --> Настройки --> Доступ к API.\n'
                  '2. Сохраните полученные ключи(повторно посмотреть ключ '
                  'будет невозможно).\n\n'
                  '✦ <b>Команда <i>/token</i> ✦:</b>\n'
                  'Позволяет сохранить или обновить API ключи видов '
                  '"Контент" и "Аналитика".\n'
                  'API ключи хранятся в нашей базе в зашифрованном виде по '
                  'стандарту AES-256, тем не менее, рекомендуется '
                  '<u>*обновлять</u> их, хотя бы, раз в 2 недели.\n'
                  'При создании API ключа для дополнительной безопасности '
                  'выберите пункт "Только для чтения", на корректность '
                  'работы бота это не повлияет.\n\n'
                  '✱ <b><u>Как пользоваться командой</u></b>:\n'
                  '1. Выберите тип сохраняемого или обновляемого токена.\n'
                  '2. Пришлите токен по запросу бота.\n'
                  '3. Токен сохранен.\n\n'
                  '* <b><u>Как обновить токен</u></b>:\n'
                  '1. Отзовите токен в личном кабинете Wildberries Partners.\n'
                  '2. Выпустите новый токен и сохраните его.\n',

    'help_get_stats': '📈 Раздел "Статистика"\n\n'
                      '✦ <b>Команда <i>/get_stats</i></b> ✦:\n'
                      'Позволяет получить статистику по одному выбранному '
                      'артикулу за выбранный период.\n'
                      'Статистика, полученная за периоды от 1 до 5 дней, '
                      'отображается в формате дней.\n'
                      'Статистика от 1 недели до 6 месяцев отображается в '
                      'формате выбранного периода и предыдущего периода '
                      'равного выбранному.\n'
                      'Выбранный период или количество дней считается от '
                      'текущей даты.\n\n'
                      '✱ <b><u>Как пользоваться командой</u></b>:\n'
                      '1. Сохраните API ключи типов "Контент" и "Аналитика".\n'
                      '2. Выберите артикул по которому Вы хотите получить '
                      'статистику.\n'
                      '3. Выберите из предложенных вариантов период для '
                      'получения статистики.\n'
                      '4. Статистика получена.',

    'help_favorites': '⭐️ Раздел "Избранное"\n\n'
                      '✦ <b>Команда <i>/favorites</i></b> ✦:\n'
                      'Позволяет выполнять избранные запросы, для удобства'
                      'и ускорения работы бота.\n\n'
                      '✱ <b><u>Как добавить запрос в избранное</u></b>:\n'
                      '1. Выполните команду /get_stats\n'
                      '2. Нажмите на ☆ до того как выберете артикул\n'
                      '3. Выберите период для получения статистики\n'
                      '4. Ваш запрос добавлен в избранное\n\n'
                      '✱ <b><u>Как выполнить избранный запрос</u></b>:\n'
                      '1. Выполните команду /favorites\n'
                      '2. Выберите нужный в списке избранных запросов.\n'
                      '3. Статистика получена\n\n'
                      '✱ <b><u>Как удалить запрос из избранного</u></b>:\n'
                      '1. Выполните команду /favorites\n'
                      '2. Нажмите на ♲ \n'
                      '3. Нажмите на запрос, который хотите удалить\n'
                      '4. Запрос удален из избранного',

    'help_cancel': '↩️ Раздел "Сброс Состояний"\n\n'
                   '✦ <b>Команда <i>/cancel</i></b> ✦:\n'
                   'Позволяет возобновить работу бота, если'
                   'в какой то момент взаимодействия что то пошло не так и он '
                   'перестал отвечать.\n\n'
                   '🙃 Надеемся эта команда вам не понадобится.',

    'help_my_limits': '💯 Раздел "Лимиты"\n\n'
                      '✦ <b>Команда <i>/my_limits</i></b> ✦:\n'
                      'Позволяет узнать количество доступных запросов.\n\n'
                      '👷‍Данный раздел находится в процессе доработки...',
}

get_stats_mess_templates: dict = {
    'make_request': 'Выполняю запрос...⌛️',
    'limit_requests': '📵 Достигнут лимит запросов.\n'
                      '🕖 Лимит будет обновлен через: {}\n\n'
                      '💡 После окончания таймера '
                      'ваш лимит будет обновлен автоматически. '
                      'Таймер на следующее обновление лимита будет запущен '
                      'после выполнения одной из этих команд:\n'
                      '- /get_stats\n'
                      '- /my_limits',

    'save_tokens': '🔐 Для выполнения данной операции необходимо '
                   'сохранить токены типов: '
                   '"Контент" и "Аналитика".\n\n'
                   '💡 Выполните команду /token и следуйте '
                   'дальнейшим инструкциям.',

    'change_nm_id': '📑 В сообщении представлены ваши номенклатуры.\n'
                    'Выберите нужный артикул и нажмите соответсвующую '
                    'кнопку на клавиатуре под ниже.\n\n',
    'send_nm_ids_template':
        '❇️  Артикул: <u>{}</u>\n'
        '🗂️  Категория: {}\n'
        '🆔  Номер номенклатуры: {}\n'
        '_________\n\n',

    'plus_send_nm_ids_template': '💡 Для получения статистики выберите '
                                 'нужный артикул ⤵️',

    'set_state_statistics_mess_template':
        'Введите числовой номер номенклатуры, '
        'для получения статистики.\n'
        'Пример: "147200496"\n',

    'set_get_period_state': '📆 Выберите период для получения статистики.\n\n'
                            '💡 От 1 до 5 дней статистика будет'
                            ' разделена по дням, '
                            'от недели и более сгруппирована по '
                            'выбранному периоду, '
                            'плюс за предыдущий период равный выбранному.',

    'product_vendor_code': '❇️ <u>Товар</u>: <i><b>{}</b></i>.\n'
                           '🆔 <u>Артикул</u>: <i><b>{}</b></i>.\n\n',
    
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

stickers = {
    'start_sticker': 'CAACAgIAAxkBAAEBjxNlNEKVb0a0gj-L-BxBs8n5FWBQ_gACbwAD29t-AAGZW1Coe5OAdDAE',
    'error_401_sticker': 'CAACAgIAAxkBAAEBjx9lNEXeF9goYdFPj6v_195o3fkZRgACXwAD29t-AAGEsFSbEa7K4zAE',
    'error_try_later_sticker': 'CAACAgIAAxkBAAEBjxVlNENylv6-XrO94jUBR82Sisq-XAACYwAD29t-AAGMnQU950KD5zAE',
    'limit_requests': 'CAACAgIAAxkBAAECXMBldPWCXWv2bAABCTixJxgZaC8gkWUAAjgAA9vbfgAB2ZN8mDds5SwzBA',
    'have_requests': 'CAACAgIAAxkBAAECZBVld5HmYoH2sIXacwOqtY8ZKLHSKAACPwAD29t-AAH05pw4AeSqaTME',
    'dont_have_requests': 'CAACAgIAAxkBAAECZBdld5IUF6wdu9MoOO_MZ1xPSVg7WQACbgAD29t-AAFGnmdxMjn-kzME'
}

get_favorite_message_templates = {
    'favorite_requests': '⭐️ Ваши избранные запросы:\n\n'
                         '💡 Выберите один из представленных ниже '
                         'для его выполнения.',
    'del_favorite_request': '⭐️ Ваши избранные запросы:\n\n'
                            '⚠️ Выберите один из представленных ниже '
                            'для его УДАЛЕНИЯ.',
    'no_favorites': '⭐️ Пока у вас нет избранных запросов.\n\n'
                    '💡 Что бы добавить запрос в избранное:\n'
                    '- Выполните команду /get_stats\n'
                    '- Нажмите на ☆ перед выбором артикула\n'
                    'Так ваш текущий запрос будет добавлен в избранное.',
    'max_limit_favorite': '🚫 Достигнут максимальный лимит запросов в '
                          'избранном.\n\n'
                          '💡 Удалите невостребованные запросы из своего '
                          'избранного и повторите попытку.'
}

save_token_mess_templates: dict = {
    'change_token_type': '‼️ Выберите тип сохраняемого/обновляемого '
                         'токена.\n\n'
                         '💡 Для работы бота необходимо сохранить токены типов'
                         ' "Контент" и "Аналитика".',
    'save_token': '🤫 Введите ваш токен "{}".',
    'token_updated': '🔑 Токены сохранены, бот готов к работе!\n'
                     'Для проверки выполните команду\n /get_stats 👌\n\n'
                     '💡 Не забывайте регулярно обновлять токены.',
    'send_token_analytic': '🔑 Токен типа "Контент" сохранен!\n'
                           'Для работы бота не хватает одного токена.\n'
                           'Выполните команду /token, и сохраните '
                           'токен "Аналитика".',
    'send_token_content': '🔑 Токен типа "Аналитика" сохранен!\n'
                          'Для работы бота не хватает одного токена.\n'
                          'Выполните команду /token, и сохраните '
                          'токен "Контент".'
}

my_limits_mess_template = {
    'my_limits': '📤 У вас осталось {} запросов.\n'
                 '🕖 Лимит будет обновлен через: {}\n\n'
                 '💡 После окончания таймера '
                 'ваш лимит будет обновлен автоматически. '
                 'Таймер на следующее обновление лимита будет запущен '
                 'после выполнения одной из этих команд:\n'
                 '- /get_stats\n'
                 '- /my_limits',
}
