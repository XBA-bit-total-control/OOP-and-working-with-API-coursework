from access_data import token_Ydisk
import requests
import json
import time
import os



class CatKeeper:
    "Класс для загрузки кото-фоток с текстом на Яндекс.Диск"
    def __init__(self, token: str):
        "Нужно передать токен для работы с Яндекс_Диском"
        self.counter = 1
        self.token = token

    def load_cat(self, quantity: int = 3, text: str = "Мурзилка PD-140"):
        """Метод загружает заданное количество фотографий в папку PD-140
        присваивает текст к каждой картинке и сохраняет технические данные в отдельный файл"""
        try:
            if isinstance(quantity, int) and 1 <= quantity <= 25:
                while bool(quantity) == True:
                    # Отсылаем запрос для получения картинки с котом и сохраняем ее
                    with open(f"image_{self.counter}.jpeg", 'wb') as fl:
                        self.responce = requests.get(f'https://cataas.com/cat/says/{text}', timeout=45)   # Повышенное время ожидания, а то бывает отвечает долго
                        fl.write(self.responce.content)

                    # Создаём папку PD-140, если её ещё нет
                    requests.put(
                        'https://cloud-api.yandex.net/v1/disk/resources',
                        headers={'Authorization': self.token},
                        params={'path': 'PD-140'}
                    )

                    # Получаем ссылку для загрузки файла на диск
                    self.down_link = requests.get(
                        'https://cloud-api.yandex.net/v1/disk/resources/upload',
                        headers={'Authorization': self.token},
                        params={'path': f'PD-140/image_{self.counter}.jpeg'}
                    ).json()["href"]

                    # Открываем и загружаем картинку на диск
                    with open(f"image_{self.counter}.jpeg", 'rb') as fl:
                        requests.post(
                            self.down_link,
                            headers={'Authorization': self.token},
                            params={
                                    'path': f'PD-140/image_{self.counter}.jpeg',
                                    'url': self.down_link
                                    },
                            files={'file': fl}
                        )

                    # Заполняем технический файл
                    with open("tech_data_cats.json", "r", encoding='utf-8') as fl:
                        self.data = fl.read()
                    with open("tech_data_cats.json", "w+t", encoding='utf-8') as f:
                        self.new = json.loads(self.data)
                        self.new.append(
                            {
                                "File_name": f"image_{self.counter}.jpeg",
                                "Completed": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                "Content_Length": str(self.responce.headers).split("', '")[3].split("': '")[1]
                            }
                        )
                        json.dump(self.new, f, ensure_ascii=False, indent=2)

                    # Удаляем картинку с компьютера, чтобы не сохранять лишние данные
                    os.remove(f"image_{self.counter}.jpeg")

                    # Для корректной итерации
                    self.counter += 1
                    quantity -= 1
                    time.sleep(1)

        # Обработка ошибок
            else:
                raise ValueError("Заданно неподдерживаемое значение или оно выше разового лимита загрузки в 25 кото-фоток")
        except KeyError:
            os.remove(f"image_{self.counter}.jpeg")
            raise FileExistsError(
                """Создаваемый файл уже существует на вашем диске!
            Для корректной работы программы измените значение счётчика, через метод .configure_counter()
            с аргументом-числом на единицу больше, чем самое большое число в имени картинки на диске.
            Или если вы хотите перезаписать его, то удалите файл с диска самостоятельно."""
            )
        except TimeoutError:
            raise TimeoutError("Сервер долго не отвечает")
        except:
            raise Exception("Незарегистрированная ошибка")

    def clear_tech_data(self):
        "Позволяет очистить данные технического файла"
        with open("tech_data_cats.json", "w") as fl:
            json.dump([], fl)

    def configure_counter(self, num : int):
        """Настройка счётчика позволяет изменить имя создаваемого файла,
        если на диске уже есть файл с таким именем - это исключает ошибку"""
        self.counter = num


# Демонстрация работы программы
my_cat = CatKeeper(token_Ydisk)
my_cat.load_cat()   # Аргументы при необходимости можно задать