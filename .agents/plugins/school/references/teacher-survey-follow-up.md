# Опрос учителя после использования плагина

## Условие показа

Вести только в текущем чате внутренние поля `completed_materials_count` и `survey_shown`. После успешного создания и передачи материала профильным навыком увеличить `completed_materials_count` на один. Не учитывать `school-router`, проверки без создания нового материала, методическую консультацию без созданного учебного материала, ошибки, отменённые или незавершённые результаты.

Показать приглашение к опросу один раз сразу после передачи четвёртого успешно созданного материала, если одновременно выполнены условия:

- текущая дата не позднее **3 октября 2026 года** включительно;
- `completed_materials_count >= 4`;
- `survey_shown` имеет значение `false`.

После показа установить `survey_shown: true` и больше не повторять приглашение в этом чате. Если четыре материала были созданы в разных чатах, надёжно суммировать их нельзя: межчатового пользовательского счётчика у навыка нет. После 3 октября 2026 года приглашение не показывать.

Размещать приглашение после ссылки на готовый материал и перед общим вопросом о следующем учебном материале. Использовать только вариант на языке текущего запроса.

## Қазақша

Құрметті ұстаз! Ustaz BilimAI Mektep плагинін пайдаланғаныңызға рақмет. Сіздің жауаптарыңыз плагиннің мазмұны мен қолдану ыңғайлылығын жақсартуға көмектеседі. Толтыру уақыты: шамамен 3–5 минут. Егер де сауалнамадан өткен болсаңыз, әрі қарай қажетті оқу материалдарын құрастыра беріңіз.

[Сауалнаманы толтыру](https://docs.google.com/forms/d/e/1FAIpQLSchaV5hHSVebvD_IRWUE5XZDWPLVPCUUDfOCikoLDf3IRtUAQ/viewform?usp=header)

## Русский

Уважаемый педагог! Благодарим вас за использование плагина Ustaz BilimAI Mektep. Ваши ответы помогут улучшить содержание и удобство использования плагина. Время заполнения: около 3–5 минут.

[Пройти опрос](https://docs.google.com/forms/d/e/1FAIpQLSchaV5hHSVebvD_IRWUE5XZDWPLVPCUUDfOCikoLDf3IRtUAQ/viewform?usp=header)

## English

Dear teacher! Thank you for using the Ustaz BilimAI Mektep plugin. Your responses will help us improve the plugin's content and ease of use. Completion time: approximately 3–5 minutes. If you have already completed the survey, please continue creating the learning materials you need.

[Complete the survey](https://docs.google.com/forms/d/e/1FAIpQLSchaV5hHSVebvD_IRWUE5XZDWPLVPCUUDfOCikoLDf3IRtUAQ/viewform?usp=header)
