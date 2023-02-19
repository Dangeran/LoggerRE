import csv
import re
import datetime

LOGFILE = 'log.txt'

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            now_time = datetime.datetime.now()
            with open(path, 'a') as log_file:
                log_file.write(f'log-time: {now_time.date()} {now_time.time()}\n')  # strftime("%H:%M:%S")
                log_file.write(f'function: {old_function.__name__}\n')
                if args:
                    log_file.write(f"arguments: {', '.join(map(str, args))}\n")
                if kwargs:
                    log_file.write(f"kw. args: {', '.join(map(str, kwargs.items()))}\n")
                result = old_function(*args, **kwargs)
                log_file.write(f'f.result: {result}\n')
            return result

        return new_function

    return __logger

@logger(LOGFILE)
def get_contact_list(file_name):
    with open(file_name, encoding="utf8") as f:
        return list(csv.reader(f, delimiter=","))

@logger(LOGFILE)
def save_contact_list(contact_list, file_name):
    with open(file_name, "w", newline='') as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(contact_list)

@logger(LOGFILE)
def order_contact_list(contact_list):
    order_contacts = []
    for contact in contact_list:
        full_name = (contact[0] + ' ' + contact[1] + ' ' + contact[2]).split()
        order_contact = [full_name[0], full_name[1]]

        if len(full_name) > 2:  # Проверка на наличие Отчества
            order_contact.append(full_name[2])
        else:
            order_contact.append('')
        order_contact.append(contact[3])
        order_contact.append(contact[4])

        pattern = r"(\+7|8){1}\s*\(*(\d{3})\)*-*\s*(\d{3})\-*\s*(\d{2})\-*\s*(\d{2})\s*\(*([доб.]*)\s*(\d{4})*\)*"
        substitution = r'+7(\2)\3-\4-\5 \6 \7'
        result = re.sub(pattern, substitution, contact[5]).rstrip()
        order_contact.append(result)

        order_contact.append(contact[6])

        order_contacts.append(order_contact)
    return order_contacts

@logger(LOGFILE)
def delete_duplicate(contact_list):
    sorted_contact_list = [contact_list[0]]
    contact_list.pop(0)

    while contact_list:
        summ_list = [0]
        lastname = contact_list[0][0]
        firstname = contact_list[0][1]
        surname = contact_list[0][2]
        organization = contact_list[0][3]
        position = contact_list[0][4]
        phone = contact_list[0][5]
        email = contact_list[0][6]

        for j in range(1, len(contact_list)):  # Находим совпадение по имени и фамилии и записываем индексы списка
            if lastname == contact_list[j][0] and firstname == contact_list[j][1]:
                summ_list.append(j)
                if contact_list[j][2] > surname:
                    surname = contact_list[j][2]
                if contact_list[j][3] > organization:
                    organization = contact_list[j][3]
                if contact_list[j][4] > position:
                    position = contact_list[j][4]
                if contact_list[j][5] > phone:
                    phone = contact_list[j][5]
                if contact_list[j][6] > email:
                    email = contact_list[j][5]

        sorted_contact_list.append([lastname, firstname, surname, organization, position, phone, email])

        summ_list.sort(reverse=True)
        for k in summ_list:
            contact_list.pop(k)

    return sorted_contact_list


if __name__ == "__main__":
    contacts = get_contact_list("phonebook_raw.csv")
    ord_contacts = order_contact_list(contacts)
    sorted_contacts = delete_duplicate(ord_contacts)
    save_contact_list(sorted_contacts, "phonebook.csv")
