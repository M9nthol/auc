import asyncio
from telebot import types
from sc_client import client
from stalcraft import LocalItem, Order, Sort
from main import bot
import threading
from time import sleep



# Общий объект события для остановки потоков
stop_event = threading.Event()

# Словарь для хранения потоков мониторинга для каждого пользователя
user_threads = {}

# Счетчик активных пользователей
active_users = 0

# Максимальное количество одновременных пользователей
MAX_USERS = 20

# Семафор для ограничения одновременных пользователей
semaphore = asyncio.Semaphore(MAX_USERS)

lock = threading.Lock()

# Словарь для отслеживания уже отправленных сообщений о снятии лота
sent_lot_removal_messages = {}


@bot.callback_query_handler(func=lambda call: call.data == "auction")
def handle_callback_query_auction(call):
    global active_users
    chat_id = call.message.chat.id

    # Проверяем, есть ли пользователь в закрытом чате
    try:
        # Используйте метод 'get_chat_member' для проверки
        member = bot.get_chat_member(chat_id=-1002098126171, user_id=call.from_user.id)

        if member.status != 'left':


            # Создаем новую инлайн-клавиатуру с типами снаряжения
            markup = types.InlineKeyboardMarkup(row_width=1)
            button_armor = types.InlineKeyboardButton(text="Броня", callback_data="armor")
            button_weapon = types.InlineKeyboardButton(text="Оружие", callback_data="weapon")
            button_cont = types.InlineKeyboardButton(text="Контейнеры", callback_data="cont")
            button_ddt = types.InlineKeyboardButton(text="Детекторы и сканеры", callback_data="ddt")
            button_art = types.InlineKeyboardButton(text="Артефакты", callback_data="art")
            button_obv = types.InlineKeyboardButton(text="Обвесы", callback_data="obv")
            markup.add(button_armor, button_weapon, button_cont, button_ddt, button_art, button_obv)


            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=f"Хорошо❗\nСейчас активных пользователей: {active_users} из 20\nВыбери направление:",
                                  reply_markup=markup)
        else:
            # Пользователь не в чате, не показываем кнопки
            bot.send_message(chat_id, 'Вы не имеете доступа к этой функции!🚫\nДля получения доступа к мониторингу необходимо оформить подписку от MoniBot :https://boosty.to/mentho1/purchase/2828670?ssource=DIRECT&share=subscription_link')
    except Exception as e:
        # Обработка ошибок
        bot.answer_callback_query(callback_query_id=call.id, text="Произошла ошибка. Попробуйте снова.")
        print(f"Ошибка при проверке пользователя в чате: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_callback_query_back(call):
    chat_id = call.message.chat.id

    # Очищаем предыдущее сообщение и выводим новое с кнопкой "Назад"
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо❗\nСейчас активных пользователей: {active_users} из 30\nВыбери направление:",
                          reply_markup=get_auction_markup())

# Функция для создания инлайн-клавиатуры с кнопками выбора типа снаряжения
def get_auction_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_armor = types.InlineKeyboardButton(text="Броня", callback_data="armor")
    button_weapon = types.InlineKeyboardButton(text="Оружие", callback_data="weapon")
    button_cont = types.InlineKeyboardButton(text="Контейнеры", callback_data="cont")
    button_ddt = types.InlineKeyboardButton(text="Детектор", callback_data="ddt")
    button_art = types.InlineKeyboardButton(text="Артефакты", callback_data="art")
    button_obv = types.InlineKeyboardButton(text="Обвесы", callback_data="obv")
    markup.add(button_armor, button_weapon, button_cont, button_ddt, button_art, button_obv)
    return markup

@bot.callback_query_handler(func=lambda call: call.data == "obv")
def handle_callback_query_obv(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a67 = types.InlineKeyboardButton(text="Магазин 7.62 30пт (черный)", callback_data="a67")
    button_a66 = types.InlineKeyboardButton(text="Барабанный магазин 5.45", callback_data="a66")
    button_a68 = types.InlineKeyboardButton(text="Барабанный магазин 5.56 NATO EMAG", callback_data="a68")
    button_a69 = types.InlineKeyboardButton(text="Увеличенный магазин АК-308", callback_data="a69")
    button_a70 = types.InlineKeyboardButton(text="Прицел коллиматорный DM", callback_data="a70")
    button_a79 = types.InlineKeyboardButton(text="Прицел оптический Sig Sauer", callback_data="a79")
    button_a80 = types.InlineKeyboardButton(text="Прицел коллиматорный Barska", callback_data="a80")

    markup.add(button_a67, button_a66, button_a68, button_a69, button_a70, button_a79, button_a80)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери обвес:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "armor")
def handle_callback_query_armor(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_veteranarmor = types.InlineKeyboardButton(text="Ветеран🟣", callback_data="veteran_armor")
    button_masterarmor = types.InlineKeyboardButton(text="Мастер 🔴", callback_data="master_armor")
    button_legendarmor = types.InlineKeyboardButton(text="Легенда🟡", callback_data="legend_armor")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_veteranarmor, button_masterarmor, button_legendarmor, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете ранг интересующей Вас брони:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "weapon")
def handle_callback_query_weapon(call):
    chat_id = call.message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_veteran = types.InlineKeyboardButton(text="Ветеран🟣", callback_data="veteran_weapon")
    button_master = types.InlineKeyboardButton(text="Мастер 🔴", callback_data="master_weapon")
    button_legend = types.InlineKeyboardButton(text="Легенда🟡", callback_data="legend_weapon")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_veteran, button_master, button_legend, button_back)

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберите ранг интересующего Вас оружия:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "veteran_armor")
def handle_callback_query_veteran_armor(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a1 = types.InlineKeyboardButton(text="Магнит", callback_data="a1")
    button_a3 = types.InlineKeyboardButton(text="Туманка", callback_data="a3")
    button_a4 = types.InlineKeyboardButton(text="Тонга", callback_data="a4")
    button_a5 = types.InlineKeyboardButton(text="Йорш", callback_data="a5")
    button_a6 = types.InlineKeyboardButton(text="Идущий в метели", callback_data="a6")
    button_a7 = types.InlineKeyboardButton(text="Спаннер", callback_data="a7")
    button_a8 = types.InlineKeyboardButton(text="Аметист", callback_data="a8")
    button_a9 = types.InlineKeyboardButton(text="Лазутчик", callback_data="a9")
    button_a10 = types.InlineKeyboardButton(text="Разведка", callback_data="a10")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_a1, button_a3, button_a4, button_a5, button_a6, button_a7, button_a8, button_a9, button_a10, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери броню:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "master_armor")
def handle_callback_query_master_armor(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a11 = types.InlineKeyboardButton(text="Зивкас", callback_data="a11")
    button_a12 = types.InlineKeyboardButton(text="Ригель", callback_data="a12")
    button_a13 = types.InlineKeyboardButton(text="КЗ-4", callback_data="a13")
    button_a14 = types.InlineKeyboardButton(text="Танк", callback_data="a14")
    button_a15 = types.InlineKeyboardButton(text="Модифицированный экзоскелет (Гектор)", callback_data="a15")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_a11, button_a12, button_a13, button_a14, button_a15, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери броню:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "legend_armor")
def handle_callback_query_legend_armor(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a32 = types.InlineKeyboardButton(text="Альбатрос-Штурмовик", callback_data="a32")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_a32, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери броню:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "veteran_weapon")
def handle_callback_query_weapon_veteran_weapon(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a16 = types.InlineKeyboardButton(text="HK PSG1", callback_data="a16")
    button_a17 = types.InlineKeyboardButton(text="СВ-98", callback_data="a17")
    button_a18 = types.InlineKeyboardButton(text="M1014 Breacher", callback_data="a18")
    button_a19 = types.InlineKeyboardButton(text="ОЦ-14М Шторм", callback_data="a19")
    button_a20 = types.InlineKeyboardButton(text="РПК-16", callback_data="a20")
    button_a21 = types.InlineKeyboardButton(text="Crye Precision SIX12", callback_data="a21")
    button_a22 = types.InlineKeyboardButton(text="АК-12", callback_data="a22")
    button_a75 = types.InlineKeyboardButton(text="Grizzly 8.5", callback_data="a75")
    button_a76 = types.InlineKeyboardButton(text="МЦ-255", callback_data="a76")
    button_a77 = types.InlineKeyboardButton(text="HK416", callback_data="a77")
    button_a78 = types.InlineKeyboardButton(text="AUG A2", callback_data="a78")
    button_a82 = types.InlineKeyboardButton(text="РМО-93", callback_data="a82")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_a16, button_a17, button_a18, button_a19, button_a20, button_a21, button_a22, button_a75, button_a76, button_a78, button_a77, button_a82, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери оружие:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "master_weapon")
def handle_callback_query_weapon_master_weapon(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_a23 = types.InlineKeyboardButton(text="Jagdkommando", callback_data="a23")
    button_a73 = types.InlineKeyboardButton(text="M48 Tomahawk", callback_data="a73")
    button_a74 = types.InlineKeyboardButton(text="Gerber Downrange Tomahawk", callback_data="a74")
    button_a24 = types.InlineKeyboardButton(text="HK XM8S", callback_data="a24")
    button_a25 = types.InlineKeyboardButton(text="АК-308", callback_data="a25")
    button_a26 = types.InlineKeyboardButton(text="AA-12", callback_data="a26")
    button_a27 = types.InlineKeyboardButton(text="ВСК-94", callback_data="a27")
    button_a28 = types.InlineKeyboardButton(text="FN FAL", callback_data="a28")
    button_a29 = types.InlineKeyboardButton(text="Scar-H", callback_data="a29")
    button_a71 = types.InlineKeyboardButton(text="HK417", callback_data="a71")
    button_a72 = types.InlineKeyboardButton(text="IWI Tavor X95", callback_data="a72")
    button_a30 = types.InlineKeyboardButton(text="ПТРД-М", callback_data="a30")
    button_a38 = types.InlineKeyboardButton(text="LR-300", callback_data="a37")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")

    markup.add(button_a23, button_a24, button_a25, button_a26, button_a27, button_a28, button_a29, button_a30,
               button_a38, button_a71, button_a72, button_a73, button_a74, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери оружие:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "legend_weapon")
def handle_callback_query_weapon_legend_weapon(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_gays = types.InlineKeyboardButton(text="Гаусс-Пушка", callback_data="a31")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_gays, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери оружие:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "ddt")
def handle_callback_query_ddt(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_elb = types.InlineKeyboardButton(text="ДУД Эльбрус", callback_data="a33")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_elb, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете интересующий Вас детектор:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "cont")
def handle_callback_query_cont(call):
    chat_id = call.message.chat.id
    # Create an inline keyboard with weapon options
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_6y = types.InlineKeyboardButton(text="Берлога 6у", callback_data="a34")
    button_4y = types.InlineKeyboardButton(text="Берлога 4у", callback_data="a35")
    button_ksm = types.InlineKeyboardButton(text="КСМ", callback_data="a36")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_4y, button_6y, button_ksm, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Выбери нужный контейнер:",
                          reply_markup=markup)


@bot.callback_query_handler(
    func=lambda call: call.data in ["a1", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10", "a11", "a12", "a13", "a14",
                                    "a15", "a16", "a17", "a18", "a19", "a20", "a21", "a22", "a23", "a24", "a25", "a26",
                                    "a27", "a28", "a29", "a30", "a31", "a32", "a33", "a34", "a35", "a36", "a37", "a66", "a67", "a68", "a69", "a70", "a71", "a72", "a73", "a74", "a75", "a76", "a77", "a78", "a79", "a80", "a82"])
def handle_callback_query_item(call):
    chat_id = call.message.chat.id
    item_id = {
        "a1": ("1rkn1"),
        "a3": ("y359o"),
        "a4": ("4qldn"),
        "a5": ("5lr4q"),
        "a6": ("qjomk"),
        "a7": ("y35l3"),
        "a8": ("ok096"),
        "a9": ("zzjgn"),
        "a10": ("knqkv"),
        "a11": ("g43rp"),
        "a12": ("kn3yv"),
        "a13": ("qj1lk"),
        "a14": ("y3q1o"),
        "a15": ("5l1q0"),
        "a16": ("okm20"),
        "a17": ("knm0v"),
        "a18": ("m0mz2"),
        "a19": ("4qnwn"),
        "a20": ("2onz6"),
        "a21": ("0r211"),
        "a22": ("g4mdp"),
        "a23": ("knvmj"),
        "a24": ("n4md3"),
        "a25": ("dmjdn"),
        "a26": ("qj2zk"),
        "a27": ("m0mo7"),
        "a28": ("5lnw0"),
        "a29": ("wj75o"),
        "a30": ("4qnyn"),
        "a31": ("knmdv"),
        "a32": ("wj4no"),
        "a33": ("gdj6"),
        "a34": ("49dj"),
        "a35": ("l3n2"),
        "a36": ("j3ml"),
        "a37": ("5ln40"),
        "a66": ("4qp1o"),
        "a67": ("ly1lo"),
        "a68": ("rw4ry"),
        "a69": ("96pwy"),
        "a70": ("3g7wg"),
        "a71": ("p63d2"),
        "a72": ("2ony6"),
        "a73": ("vj427"),
        "a74": ("y3j20"),
        "a75": ("6w64y"),
        "a76": ("rw2ky"),
        "a77": ("dmjwn"),
        "a78": ("969jz"),
        "a79": ("5lv9o"),
        "a80": ("j56d6"),
        "a82": ("RMB-93")




    }[call.data]

    # Проверяем, есть ли у пользователя активный мониторинг
    if chat_id in user_threads:
        bot.send_message(chat_id,
                         "Вы уже мониторите лот❗\nОстановите мониторинг текущего лота, чтобы начать отслеживать новый.\nЧтобы остановить пропишите команду /stop")
        return

    # Проверяем, есть ли места для нового пользователя
    if active_users >= MAX_USERS:
        bot.send_message(chat_id, f"Слишком много пользователей. Дождитесь, когда освободится место.")
        return

    bot.send_message(chat_id, "Введите максимальную желаемую цену выкупа (в рублях, например 100000)")

    # Создаем локальную функцию для обработки цены выкупа
    def handle_buyout_price(message, chat_id, item_id):
        global active_users
        try:
            buyout_price = int(message.text)

            with lock:
                # Проверяем, есть ли уже поток для этого пользователя
                if chat_id in user_threads:
                    # Останавливаем старый поток
                    user_threads[chat_id].stop_event.set()
                    user_threads[chat_id].join()
                    del user_threads[chat_id]
                    active_users -= 1
                    print(
                        f"Остановлен старый поток для пользователя {chat_id}. Активные пользователи: {active_users}")

                    # Создаем новый поток
                stop_event = threading.Event()
                thread = threading.Thread(target=monitor_lots,
                                          args=(chat_id, item_id, buyout_price, stop_event))
                thread.stop_event = stop_event  # Добавили stop_event как атрибут
                user_threads[chat_id] = thread
                thread.start()
                active_users += 1
                print(f"Запущен новый поток для пользователя {chat_id}. Активные пользователи: {active_users}")
                bot.send_message(chat_id,
                                 "✅️Оповещения активированы✅️\nЯ буду отслеживать лоты с ценой выкупа ниже или равной заданной.")

        except ValueError:
            bot.send_message(chat_id,
                             "⚠️Ошибка⚠️\nВы ввели не целое число❗\nПопробуйте снова, нажав на нужный предмет и введя целое число, например 100000.")

        # Регистрируем локальный обработчик сообщений для текущего пользователя и предмета

    bot.register_next_step_handler(call.message, handle_buyout_price, chat_id, item_id)


@bot.message_handler(commands=['stop'])
def handle_stop_command(message):
    chat_id = message.chat.id
    with lock:  # Используем lock для блокировки
        # Проверяем, есть ли запущенный поток для данного пользователя
        if chat_id in user_threads:
            # Отправляем сообщение о том, что мониторинг останавливается
            bot.send_message(chat_id, "Понял👌, cейчас остановлю мониторинг, пожалуйста дождись моего сообщения...")

            # Останавливаем поток
            user_threads[chat_id].stop_event.set()  # Устанавливаем локальный Event
            # Добавлен join() чтобы ждать завершения потока
            user_threads[chat_id].join()
            # Удалите элемент из user_threads *после* завершения потока
            del user_threads[chat_id]

            global active_users
            active_users -= 1  # Уменьшаем active_users после остановки потока
            print(f"Активные пользователи: {active_users}")
            bot.send_message(chat_id, "⛔️Оповещения остановлены⛔️\nТеперь можешь запустить другой мониторинг или узнать актуальные лоты на аукционе!")
        else:
            # Если поток не был запущен, просто сообщаем пользователю
            bot.send_message(chat_id, "⚠️Оповещения не были запущены.⚠️")


def monitor_lots(chat_id, item_id, buyout_price, stop_event):
    lp = []
    previous_lots = []  # Список лотов из предыдущей итерации
    sent_lot_removal_messages = {}  # Словарь для отслеживания сообщений об удалении лотов

    # Цикл, который проверяет флаг остановки
    while not stop_event.is_set():
        lots = client.auction(item_id).lots(limit=10, sort=Sort.BUYOUT_PRICE, order=Order.ASC, additional=True)
        print(f"это предметы")

        # Проверяем удаленные лоты
        for previous_lot in previous_lots:
            if previous_lot not in lots:
                # Проверка, отправлено ли уже сообщение об удалении этого лота
                if (chat_id, previous_lot.item_id, previous_lot.buyout_price) not in sent_lot_removal_messages:
                    # Проверяем, была ли цена выкупа лота меньше или равна заданной пользователем И НЕ равна 0
                    if previous_lot.buyout_price <= buyout_price and previous_lot.buyout_price > 0:
                        bot.send_message(chat_id,
                                         f"❗Внимание❗\nЛот,который был с ценой выкупа💵: {previous_lot.buyout_price}\nВыкупили или сняли с продажи❗")
                        sent_lot_removal_messages[(chat_id, previous_lot.item_id,
                                                   previous_lot.buyout_price)] = True  # Отметка, что сообщение об удалении лота отправлено

        # Обновляем список лотов из предыдущей итерации
        previous_lots = lots

        for lot in lots:
            # Проверяем, есть ли цена выкупа и она меньше или равна заданной, и НЕ равна 0
            if lot.buyout_price > 0 and lot.buyout_price <= buyout_price:
                if lp.count(lot) == 0:
                    start_time_str = lot.start_time.strftime('%Y-%m-%d %H:%M:%S')
                    end_time_str = lot.end_time.strftime('%Y-%m-%d %H:%M:%S')
                    formatted_buyout_price = "{:,.0f}".format(lot.buyout_price).replace(",", ".")
                    seller_name = lot.additional.get('buyer', 'Неизвестно')

                    message_text = f"❗Найден новый лот❗\nЦена выкупа: {formatted_buyout_price}💵 \nВремя создания лота: {start_time_str}🚩\nВремя завершения лота: {end_time_str}⏳\nПродавец: {seller_name}\n\n"

                    bot.send_message(chat_id, message_text)

                    lp.append(lot)
        # Sleep for 15 seconds before making a new request
        sleep(20)
    # Сбрасываем событие остановки
    stop_event.clear()

@bot.callback_query_handler(func=lambda call: call.data == "art")
def handle_callback_query_art(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_elc = types.InlineKeyboardButton(text="Электрофизические⚡️", callback_data="elc")
    button_term = types.InlineKeyboardButton(text="Термические🔥", callback_data="term")
    button_grav = types.InlineKeyboardButton(text="Гравитационные🌌", callback_data="grav")
    button_bio = types.InlineKeyboardButton(text="Биохимические☣️", callback_data="bio")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_elc, button_term, button_grav, button_bio, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете тип артефакта:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "bio")
def handle_callback_query_bio(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_zm = types.InlineKeyboardButton(text="Змеиный глаз", callback_data="a61")
    button_se = types.InlineKeyboardButton(text="Стальной Ежик", callback_data="a62")
    button_er = types.InlineKeyboardButton(text="Ершик", callback_data="a63")
    button_mn = types.InlineKeyboardButton(text="Многогранник", callback_data="a64")
    button_err = types.InlineKeyboardButton(text="Ежик", callback_data="a65")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_zm, button_se, button_er, button_mn, button_err, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете  артефакт:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "grav")
def handle_callback_query_grav(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_proto = types.InlineKeyboardButton(text="Протоцибуля", callback_data="a53")
    button_roza = types.InlineKeyboardButton(text="Проклятая роза", callback_data="a54")
    button_nt = types.InlineKeyboardButton(text="Янтарник", callback_data="a55")
    button_kr = types.InlineKeyboardButton(text="Креветка", callback_data="a56")
    button_br = types.InlineKeyboardButton(text="Браслет", callback_data="a57")
    button_temn = types.InlineKeyboardButton(text="Темный кристалл", callback_data="a58")
    button_ost = types.InlineKeyboardButton(text="Остов", callback_data="a59")
    button_prim = types.InlineKeyboardButton(text="Золотистая Прима", callback_data="a60")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_proto, button_roza, button_nt, button_kr, button_br, button_temn, button_ost, button_prim, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете  артефакт:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "term")
def handle_callback_query_term(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_pt = types.InlineKeyboardButton(text="Жар-птица", callback_data="a46")
    button_r = types.InlineKeyboardButton(text="Радиатор", callback_data="a47")
    button_s = types.InlineKeyboardButton(text="Солнце", callback_data="a48")
    button_v = types.InlineKeyboardButton(text="Ветка Калины", callback_data="a49")
    button_k = types.InlineKeyboardButton(text="Каблук", callback_data="a50")
    button_f = types.InlineKeyboardButton(text="Фаренгейт", callback_data="a51")
    button_vi = types.InlineKeyboardButton(text="Вихрь", callback_data="a52")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_pt, button_r, button_s, button_v, button_k, button_f, button_vi, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text="Хорошо! Теперь выберете  артефакт:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "elc")
def handle_callback_query_elc(call):
    chat_id = call.message.chat.id
    # Создаем новую инлайн-клавиатуру с рангами брони
    markup = types.InlineKeyboardMarkup(row_width=1)
    button_spir = types.InlineKeyboardButton(text="Спираль", callback_data="a39")
    button_atm = types.InlineKeyboardButton(text="Атом", callback_data="a38")
    button_osk = types.InlineKeyboardButton(text="Осколок", callback_data="a41")
    button_priz = types.InlineKeyboardButton(text="Призма", callback_data="a42")
    button_zer = types.InlineKeyboardButton(text="Зеркало", callback_data="a44")
    button_gel = types.InlineKeyboardButton(text="Гелий", callback_data="a43")
    button_tran = types.InlineKeyboardButton(text="Трансформатор", callback_data="a45")
    button_back = types.InlineKeyboardButton(text="Назад⬇️", callback_data="back")
    markup.add(button_spir, button_atm, button_osk, button_priz, button_zer, button_gel, button_tran, button_back)
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Хорошо! Теперь выберете артефакт:",
                          reply_markup=markup)




@bot.callback_query_handler(
    func=lambda call: call.data in ["a38", "a39", "a41", "a42", "a43", "a44", "a45", "a46", "a47", "a48", "a49", "a50", "a51", "a52", "a53", "a54", "a55", "a56", "a57", "a58", "a59", "60", "a61", "a62", "a63", "a64", "a65"])
def handle_callback_query_item_art(call):
    chat_id = call.message.chat.id
    item_id = {
        "a38": LocalItem("Atom"),
        "a39": LocalItem("Spiral"),
        "a41": LocalItem("Shard"),
        "a42": LocalItem("Prism"),
        "a43": LocalItem("Helium"),
        "a44": LocalItem("Mirror"),
        "a45": LocalItem("Transformer"),
        "a46": LocalItem("Пламя"),
        "a47": LocalItem("Радиатор"),
        "a48": LocalItem("Солнце"),
        "a49": LocalItem("Мамины бусы"),
        "a50": LocalItem("Каблук"),
        "a51": LocalItem("Фаренгейт"),
        "a52": LocalItem("Вихрь"),
        "a53": LocalItem("Протомедуза"),
        "a54": LocalItem("Темная медуза"),
        "a55": LocalItem("Янтарник"),
        "a56": LocalItem("Золотая рыбка"),
        "a57": LocalItem("Браслет"),
        "a58": LocalItem("Черный кристалл"),
        "a59": LocalItem("Остов"),
        "a60": LocalItem("Золотистый грави"),
        "a61": LocalItem("Светляк"),
        "a62": LocalItem("Стальной колобок"),
        "a63": LocalItem("Морской еж"),
        "a64": LocalItem("Многогранник"),
        "a65": LocalItem("Колобок")

    }[call.data]

    # Проверяем, есть ли у пользователя активный мониторинг
    if chat_id in user_threads:
        bot.send_message(chat_id,
                         "Вы уже мониторите лот❗\nОстановите мониторинг текущего лота, чтобы начать отслеживать новый.\nЧтобы остановить пропишите команду /stop")
        return

    # Проверяем, есть ли места для нового пользователя
    if active_users >= MAX_USERS:
        bot.send_message(chat_id, f"Слишком много пользователей. Дождитесь, когда освободится место.")
        return

    # Запрашиваем качество
    bot.send_message(chat_id, "Введите желаемое качество цифрой,где:\n\n0-Обычный ⚪\n\n1-Необычный 🟢\n\n2-Особый 🔵\n\n3-Редкий 🟣\n\n4-Исключительный🔴\n\n5-Легендарный 🟡")

    # Создаем локальную функцию для обработки качества
    def handle_qlt(message, chat_id, item_id):
        try:
            qlt = int(message.text)
            if qlt < 0 or qlt > 5:
                bot.send_message(chat_id, "⚠️Ошибка⚠️\nКачество должно быть от 0 до 5. Попробуйте снова.")
                return

            bot.send_message(chat_id, "Введите максимальную желаемую цену выкупа (в рублях, например 100000)")

            # Создаем локальную функцию для обработки цены выкупа
            def handle_buyout_price_art(message, chat_id, item_id, qlt):
                global active_users
                try:
                    buyout_price = int(message.text)

                    with lock:  # Используем lock только здесь
                        # Проверяем, есть ли уже поток для этого пользователя
                        if chat_id in user_threads:
                            # Останавливаем старый поток
                            user_threads[chat_id].stop_event.set()
                            user_threads[chat_id].join()
                            del user_threads[chat_id]
                            active_users -= 1  # Уменьшаем active_users
                            print(
                                f"Остановлен старый поток для пользователя {chat_id}. Активные пользователи: {active_users}")

                            # Создаем новый поток
                        stop_event = threading.Event()
                        thread = threading.Thread(target=monitor_lots_art,  # Изменено на monitor_lots_art
                                                  args=(chat_id, item_id, buyout_price, qlt, stop_event))
                        thread.stop_event = stop_event  # Добавили stop_event как атрибут
                        user_threads[chat_id] = thread
                        thread.start()
                        active_users += 1
                        print(f"Запущен новый поток для пользователя {chat_id}. Активные пользователи: {active_users}")
                        bot.send_message(chat_id,
                                         "✅️Оповещения активированы✅️\nЯ буду отслеживать лоты с ценой выкупа ниже или равной заданной.")

                except ValueError:
                    bot.send_message(chat_id,
                                     "⚠️Ошибка⚠️\nВы ввели не целое число❗\nПопробуйте снова, нажав на нужный предмет и введя целое число, например 100000.")

                # Регистрируем локальный обработчик сообщений для текущего пользователя и предмета

            bot.register_next_step_handler(call.message, handle_buyout_price_art, chat_id, item_id, qlt)

        except ValueError:
            bot.send_message(chat_id,
                                "⚠️Ошибка⚠️\nВы ввели не целое число❗\nПопробуйте снова, нажав на нужный предмет и введя целое число, например 1.")

    # Регистрируем локальный обработчик сообщений для текущего пользователя и предмета
    bot.register_next_step_handler(call.message, handle_qlt, chat_id, item_id)




# Модифицированная функция monitor_lots
def monitor_lots_art(chat_id, item_id, buyout_price, qlt, stop_event):
    lp = []
    previous_lots = []  # Список лотов из предыдущей итерации
    sent_lot_removal_messages = {}  # Словарь для отслеживания сообщений об удалении лотов
    message_count = 0  # Счетчик отправленных сообщений

    # Цикл, который проверяет флаг остановки
    while not stop_event.is_set():
        lots = client.auction(item_id).lots(limit=200, sort=Sort.BUYOUT_PRICE, order=Order.ASC, additional=True)
        print("Это арты")


        # Фильтруем previous_lots по качеству
        filtered_previous_lots = [lot for lot in previous_lots if 'qlt' in lot.additional and int(lot.additional['qlt']) == qlt]

        # Проверяем удаленные лоты
        for previous_lot in filtered_previous_lots:
            if previous_lot not in lots:
                # Проверка, отправлено ли уже сообщение об удалении этого лота
                if (chat_id, previous_lot.item_id, previous_lot.buyout_price) not in sent_lot_removal_messages:
                    # Проверяем, была ли цена выкупа лота меньше или равна заданной пользователем И НЕ равна 0
                    if previous_lot.buyout_price <= buyout_price and previous_lot.buyout_price > 0:
                        bot.send_message(chat_id,
                                         f"❗Внимание❗\nЛот,который был с ценой выкупа💵: {previous_lot.buyout_price}\nВыкупили или сняли с продажи❗")
                        sent_lot_removal_messages[(chat_id, previous_lot.item_id,
                                                   previous_lot.buyout_price)] = True  # Отметка, что сообщение об удалении лота отправлено

        # Обновляем список лотов из предыдущей итерации
        previous_lots = lots

        for lot in lots:
            if 'qlt' in lot.additional:
                lot_qlt = int(lot.additional['qlt'])
            else:
                lot_qlt = 0
            if lot_qlt == qlt:
                # Проверяем, есть ли цена выкупа и она меньше или равна заданной, и НЕ равна 0
                if lot.buyout_price > 0 and lot.buyout_price <= buyout_price:
                    if lp.count(lot) == 0:
                        # Проверяем ограничение по сообщениям
                        if message_count < 10:
                            start_time_str = lot.start_time.strftime('%Y-%m-%d %H:%M:%S')
                            end_time_str = lot.end_time.strftime('%Y-%m-%d %H:%M:%S')
                            formatted_buyout_price = "{:,.0f}".format(lot.buyout_price).replace(",", ".")
                            art_qlt = lot.additional.get('qlt', 'Неизвестно')


                            message_text = f"❗Найден новый лот с качеством {art_qlt}❗\nЦена выкупа: {formatted_buyout_price}💵 \nВремя создания лота: {start_time_str}🚩\nВремя завершения лота: {end_time_str}⏳\n\n"

                            bot.send_message(chat_id, message_text)

                            lp.append(lot)
                            message_count += 1  # Увеличиваем счетчик сообщений
                        else:
                            print(f"Достигнут лимит в 10 сообщений для пользователя {chat_id}")
                            # Вы можете добавить логику для оповещения пользователя, например,
                            # bot.send_message(chat_id, "Достигнут лимит в 10 сообщений. Мониторинг продолжается.")
        # Sleep for 15 seconds before making a new request
        sleep(20)
        message_count = 0
    # Сбрасываем событие остановки
    stop_event.clear()