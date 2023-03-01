import uuid
#ALTER TABLE `product` CHANGE `left_in_stock` `left_in_stock` INT(11) NOT NULL DEFAULT '0';
import pymysql as pymysql
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox
import xlsxwriter
from bruh_ui import Ui_MainWindow
import datetime
from datetime import datetime
import os
if True:
    conn = pymysql.connect(host="localhost", user="root", passwd="", database="pos")
else:
    print("pirating bad son")
    conn = pymysql.connect(host="localhost", user="root", passwd="", database="pos")

id_of_current_transaction = None
id_of_current_customer = None
res1 = None
bruh = 1
t = []

def timeConversion(s):
    if "PM" in s:
        s = s.replace("PM", " ")
        t = s.split(":")
        if t[0] != '12':
            t[0] = str(int(t[0]) + 12)
            s = (":").join(t)
        return s
    else:
        s = s.replace("AM", " ")
        t = s.split(":")
        if t[0] == '12':
            t[0] = '00'
            s = (":").join(t)
        return s.strip()

def displaying_cursor_in_table(self, cursor,scanned_table):
    scanned_table.setRowCount(0)
    for row_number, row_data in enumerate(cursor):
        scanned_table.insertRow(row_number)
        for column_number, data in enumerate(row_data):
            scanned_table.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))


class windows(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.cancel_btn.setEnabled(0)
        self.validate_btn.setEnabled(0)
        # self.add_btn.setEnabled(0)
        self.scanned_table.setColumnWidth(0, 400)
        self.scanned_table.setColumnWidth(1, 150)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS `customer_debt_history` ( `id` INT NOT NULL AUTO_INCREMENT, `customer_id` INT NOT NULL , `debt` INT NOT NULL , `date_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS `product` ( `id` INT NOT NULL AUTO_INCREMENT , `name` VARCHAR(50) NOT NULL ,`whole_sale_price` INT(11) NOT NULL , `retail_price` INT(11) NOT NULL ,`left_in_stock` INT(11) NOT NULL DEFAULT '0' , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS `pr_in_transaction` ( `id` INT NOT NULL AUTO_INCREMENT , `product_id` INT(11) NOT NULL , `sold_whole_sale_price` BIGINT(20) NOT NULL , `sold_retail_price` BIGINT(20) NOT NULL , `quantity` INT(11) NOT NULL , `transaction_id` INT(11) NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS `transactions` ( `id` INT NOT NULL AUTO_INCREMENT , `date_and_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , `customer_id` INT NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS `customer` ( `id` INT NOT NULL AUTO_INCREMENT , `Name` VARCHAR(50) NULL , `Phone_number` VARCHAR(15) NOT NULL , `Debt` INT(255) NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("CREATE TABLE IF NOT EXISTS `fournisseur` ( `id` INT NOT NULL AUTO_INCREMENT , `Name` VARCHAR(50) NULL , `Phone_number` VARCHAR(15) NOT NULL , `Debt` INT(255) NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        cursor.execute("update product set left_in_stock = 0 where left_in_stock <= 0")
        cursor.execute("CREATE TABLE IF NOT EXISTS `fournisseur_debt_history` ( `id` INT NOT NULL AUTO_INCREMENT , `fournisseur_id` INT NOT NULL , `debt` INT(255) NOT NULL , `date_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`id`)) ENGINE = InnoDB;")
        conn.commit()

        self.start_btn.clicked.connect(self.infinit_loop_new)

        self.cancel_btn.clicked.connect(self.cancel)
        self.validate_btn.clicked.connect(self.validate)
        self.search_attendances_btn.clicked.connect(self.display_search)
        self.product_display_table.setColumnWidth(0,290)
        self.product_display_table.setColumnWidth(1,150)

        self.product_display_table.setColumnWidth(2,150)
        self.product_display_table.setColumnWidth(4,175)
        self.display_all_btn.clicked.connect(self.display_all)
        self.benefit_btn.clicked.connect(self.calculate_benefit)
        self.pr_table.setColumnWidth(0,360)
        self.pr_table.setColumnWidth(1, 100)
        self.pr_table.setColumnWidth(2, 100)
        self.pr_table_2.setColumnWidth(0, 360)
        self.pr_table_2.setColumnWidth(1, 150)
        self.pr_table_2.setColumnWidth(2, 150)

        self.fournisseur_table.setColumnWidth(0,200)
        self.fournisseur_table.setColumnWidth(1,140)



        self.quantity_txt.setText("1")
        self.quantity_txt_2.setText("1")
        self.refresh_btn.clicked.connect(self.refresh)
        self.insert_btn.clicked.connect(self.insert_product)
        self.delete_btn.clicked.connect(self.delete_product)
        # self.add_btn.clicked.connect(self.add_custom_item)
        self.check_debt.clicked.connect(self.display_debt_customers)
        self.code_txtview.textChanged[str].connect(self.search)
        self.code_txtview_2.textChanged[str].connect(self.adding_search)

        self.add_stock.clicked.connect(self.adding_stock)
        self.verse_btn.clicked.connect(self.verse_customer)
        self.add_client_btn.clicked.connect(self.add_client)
        self.add_fournisseur_btn.clicked.connect(self.add_fournisseur)
        self.delete_fournisseur_btn.clicked.connect(self.delete_fournisseur)
        self.fournisseur_check_debt.clicked.connect(self.display_debt_fournisseur)
        self.fournisseur_verse_btn.clicked.connect(self.verse_fournisseur)
        self.anti_fournisseur_verse_btn.clicked.connect(self.add_debt_fournisseur)

        self.refresh_fournisseur()
        self.choice_list.clicked.connect(self.click)

        self.choice_list_2.clicked.connect(self.click2)

        cursor.execute("select name from product")
        all_prd = cursor.fetchall()
        self.update(all_prd)
        self.update2(all_prd)


        self.refresh_clients()

        self.customer_name_choice_verse.activated[str].connect(self.display_debt_history)
        self.fournisseur_name_choice.activated[str].connect(self.display_debt_history_fournisseur)
        self.delete_client_btn.clicked.connect(self.delete_client)




    def update_label(self):
        # cur_time = datetime.strftime(datetime.now(), "%d.%m %H:%M:%S")
        self.notification_label.setText("")
        self.timer.stop()


    def add_debt_fournisseur(self):
        if self.fournisseur_anti_versement_txt.text() != '' and int(self.fournisseur_anti_versement_txt.text()) > 0:
            cursor = conn.cursor()
            cursor.execute("select debt from fournisseur where name = '"+str(self.fournisseur_name_choice.currentText())+"'")
            f = cursor.fetchall()
            added_debt = f[0][0] + int(self.fournisseur_anti_versement_txt.text())
            cursor.execute("update fournisseur set debt = '"+str(added_debt)+"' where name = '"+str(self.fournisseur_name_choice.currentText())+"'")
            cursor.execute("select id from fournisseur where name = '"+str(self.fournisseur_name_choice.currentText())+"'")
            f = cursor.fetchall()
            cursor.execute("insert into fournisseur_debt_history (fournisseur_id,debt) values ('"+str(f[0][0])+"','"+str(added_debt)+"') ")
            conn.commit()
            self.fournisseur_anti_versement_txt.setText("")
            self.show_message_box("success", "Versement à succès")
            self.display_debt_fournisseur()

    def refresh_clients(self):
        self.customer_name_choice.clear()
        self.customer_name_choice_verse.clear()
        cursor = conn.cursor()
        cursor.execute('select name from customer')
        cus_names = cursor.fetchall()
        i = 0
        while i < len(cus_names):
            self.customer_name_choice.addItem(cus_names[i][0])
            self.customer_name_choice_verse.addItem(cus_names[i][0])
            i = i + 1
    def refresh_fournisseur(self):
        self.fournisseur_name_choice.clear()
        cursor = conn.cursor()
        cursor.execute('select name from fournisseur')
        cus_names = cursor.fetchall()
        i = 0
        while i < len(cus_names):
            self.fournisseur_name_choice.addItem(cus_names[i][0])
            i = i + 1

    def delete_client(self):
        cursor = conn.cursor()
        if cursor.execute("select id from customer where name = '"+str(self.client_name_txt.text())+"'"):
            cursor.execute("delete from customer where name = '"+str(self.client_name_txt.text())+"'")
        self.client_name_txt.setText("")
        self.display_debt_customers()
        conn.commit()
        self.client_phone_txt.setText('')
        self.client_name_txt.setText('')
        self.refresh_clients()
    def delete_fournisseur(self):
        cursor = conn.cursor()
        if cursor.execute("select id from fournisseur where name = '"+str(self.fournisseur_name_txt.text())+"'"):
            cursor.execute("delete from fournisseur where name = '"+str(self.fournisseur_name_txt.text())+"'")
        self.fournisseur_name_txt.setText("")
        self.display_debt_fournisseur()
        conn.commit()
        self.fournisseur_phone_txt.setText('')
        self.fournisseur_name_txt.setText('')
        self.refresh_fournisseur()

    def add_client(self):
        if self.client_name_txt.text() != "" and self.client_phone_txt.text() != "":
            cursor = conn.cursor()
            if cursor.execute("select id from customer where name ='"+str(self.client_name_txt.text())+"'"):
                cursor.execute("update customer set phone_number = '"+str(self.client_phone_txt.text())+"' where name = '"+str(self.client_name_txt.text())+"'")
            else:
                cursor.execute("insert into customer (name,phone_number,debt) values ('"+str(self.client_name_txt.text())+"','"+str(self.client_phone_txt.text())+"','0')")
            conn.commit()
            self.client_phone_txt.setText('')
            self.client_name_txt.setText('')
            self.refresh_clients()
            self.display_debt_customers()
    def add_fournisseur(self):
        if self.fournisseur_name_txt.text() != "" and self.fournisseur_phone_txt.text() != "":
            cursor = conn.cursor()
            if cursor.execute("select id from fournisseur where name ='"+str(self.fournisseur_name_txt.text())+"'"):
                cursor.execute("update fournisseur set phone_number = '"+str(self.fournisseur_phone_txt.text())+"' where name = '"+str(self.fournisseur_name_txt.text())+"'")
            else:
                cursor.execute("insert into fournisseur (name,phone_number,debt) values ('"+str(self.fournisseur_name_txt.text())+"','"+str(self.fournisseur_phone_txt.text())+"','0')")
            conn.commit()
            self.fournisseur_phone_txt.setText('')
            self.fournisseur_name_txt.setText('')
            self.refresh_fournisseur()
            self.display_debt_fournisseur()


    def adding_stock(self):
        cursor = conn.cursor()
        if self.code_txtview_2.text() != '' or self.code_txtview_2 != '':
            if cursor.execute("select left_in_stock from product where name = '"+str(self.code_txtview_2.text())+"'"):
                quantity = cursor.fetchall()[0][0]
                quantity = quantity + int(self.quantity_txt_2.text())
                cursor.execute("update product set left_in_stock = '" + str(quantity) + "' where name = '" + str(
                    self.code_txtview_2.text()) + "'")
                conn.commit()
                self.show_message_box('Success', 'stock added')
                self.code_txtview_2.setText("")
                self.quantity_txt_2.setText('1')
                self.refresh()

        cursor.execute("update product set left_in_stock = 0 where left_in_stock <= 0")

    def display_debt_history(self):
        cursor = conn.cursor()
        cursor.execute("select customer.name,customer_debt_history.date_time,customer_debt_history.debt from customer inner join customer_debt_history on customer_debt_history.customer_id = customer.id where customer.name = '"+str(self.customer_name_choice_verse.currentText())+"'")
        result = cursor.fetchall()
        displaying_cursor_in_table(self,result,self.pr_table_2)
    def display_debt_history_fournisseur(self):
        cursor = conn.cursor()
        cursor.execute("select fournisseur.name,fournisseur_debt_history.date_time,fournisseur_debt_history.debt from fournisseur inner join fournisseur_debt_history on fournisseur_debt_history.fournisseur_id = fournisseur.id where fournisseur.name = '"+str(self.fournisseur_name_choice.currentText())+"'")
        result = cursor.fetchall()
        displaying_cursor_in_table(self,result,self.fournisseur_table)
    def display_debt_customers(self):
        cursor = conn.cursor()
        cursor.execute("select name,phone_number,debt from customer")
        result = cursor.fetchall()
        displaying_cursor_in_table(self,result,self.pr_table_2)
    def display_debt_fournisseur(self):
        cursor = conn.cursor()
        cursor.execute("select name,phone_number,debt from fournisseur")
        result = cursor.fetchall()
        displaying_cursor_in_table(self,result,self.fournisseur_table)
    def verse_customer(self):
        if self.versement_txt.text() != '' and int(self.versement_txt.text())>0:
            cursor = conn.cursor()
            cursor.execute("select debt,id from customer where name = '" + str(
                self.customer_name_choice_verse.currentText()) + "'")
            old_debt = cursor.fetchall()
            debt = old_debt[0][0] - int(self.versement_txt.text())
            if debt > 0:
                cursor.execute("update customer set debt = '" + str(debt) + "' where name = '" + str(
                    self.customer_name_choice_verse.currentText()) + "'")
                cursor.execute(
                    "insert into customer_debt_history (customer_id,debt) values ('" + str(
                        old_debt[0][1]) + "','" + str(
                        debt) + "')")
                conn.commit()
                self.show_message_box("success", "Versement à succès")
                self.versement_txt.setText('')
                self.display_debt_customers()


        else:
            self.versement_txt.setText('')

    def verse_fournisseur(self):
        if self.fournisseur_versement_txt.text() != '' and int(self.fournisseur_versement_txt.text())>0:
            cursor = conn.cursor()
            cursor.execute("select debt,id from fournisseur where name = '" + str(
                self.fournisseur_name_choice.currentText()) + "'")
            old_debt = cursor.fetchall()
            debt = old_debt[0][0] - int(self.fournisseur_versement_txt.text())
            if debt > 0:
                cursor.execute("update fournisseur set debt = '" + str(debt) + "' where name = '" + str(
                    self.fournisseur_name_choice.currentText()) + "'")
                cursor.execute(
                    "insert into fournisseur_debt_history (fournisseur_id,debt) values ('" + str(
                        old_debt[0][1]) + "','" + str(
                        debt) + "')")
                conn.commit()
                self.show_message_box("success", "Versement à succès")
                self.fournisseur_versement_txt.setText('')
                self.display_debt_fournisseur()

        else:
            self.versement_txt.setText('')


    def adding_search(self):
        typed = self.code_txtview_2.text()
        cursor = conn.cursor()
        cursor.execute("select name from product")
        all_prd = cursor.fetchall()
        if typed == '':
            data = all_prd
        else:
            data = []
            i = 0
            while i < len(all_prd):
                if typed.lower() in all_prd[i][0].lower():
                    data.append(all_prd[i][0])
                i = i + 1
        self.update2(data)

    def search(self):
        typed = self.code_txtview.text()
        cursor = conn.cursor()
        cursor.execute("select name from product")
        all_prd = cursor.fetchall()
        if typed == '':
            data = all_prd
        else:
            data = []
            i = 0
            while i < len(all_prd):
                if typed.lower() in all_prd[i][0].lower():
                    data.append(all_prd[i][0])
                i = i + 1
        self.update(data)

        if bruh == 0:
            query = "select id,whole_sale_price,retail_price,left_in_stock from product where name ='" + str(
                self.code_txtview.text()) + "'"

            if cursor.execute(query) != 0:
                result = cursor.fetchall()
                pr_id = result[0][0]
                pr_wsp = result[0][1]
                pr_rp = result[0][2]
                pr_lis = result[0][3]
                # print("products left in stock = "+str(pr_lis))

                if cursor.execute("select pr_in_transaction.quantity FROM product INNER JOIN pr_in_transaction ON product.id = pr_in_transaction.product_id  where product.id ='" + str(
                            pr_id) + "' and pr_in_transaction.transaction_id ='" + str(
                            id_of_current_transaction) + "'"):
                    res1 = cursor.fetchall()
                    quan = res1[0][0] + int(self.quantity_txt.text())
                    if quan < 0:
                        self.quantity_txt.setText(str(-res1[0][0]))
                        quan = 0
                    if pr_lis != 0 or int(self.quantity_txt.text())<0:
                        if pr_lis >= int(self.quantity_txt.text()):

                            # print("quan is = "+str(quan))

                            query = "update pr_in_transaction inner join product on product.id = pr_in_transaction.product_id set pr_in_transaction.quantity = '" + str(
                                quan) + "' where product.id = " + str(pr_id)
                            cursor.execute(query)
                            stock = pr_lis - int(self.quantity_txt.text())
                            # print("stock is "+ str(stock))
                            cursor.execute("update product set left_in_stock = '" + str(stock) + "' where id = '" + str(pr_id) + "'")
                        else:

                            quan = res1[0][0] + pr_lis
                            if quan < 0:
                                quan = 0
                                self.quantity_txt.setText("1")
                            query = "update pr_in_transaction inner join product on product.id = pr_in_transaction.product_id set pr_in_transaction.quantity = '" + str(
                                quan) + "' where product.id = " + str(pr_id)
                            cursor.execute(query)
                            cursor.execute(
                                "update product set left_in_stock = '0' where id = '" + str(pr_id) + "'")
                    else:
                        # self.notification_label.setText('No stock left')
                        self.notification_label.setText('ليس في المخزن')


                        self.timer = QTimer()
                        self.timer.timeout.connect(self.update_label)
                        self.timer.start(2000)
                        # print('no stock left of that one chief')
                else:
                    if int(self.quantity_txt.text()) <= 0:
                        self.quantity_txt.setText("1")
                    if pr_lis != 0:
                        if pr_lis >= int(self.quantity_txt.text()):
                            cursor.execute(
                                "INSERT INTO pr_in_transaction (product_id,quantity,transaction_id,sold_whole_sale_price,sold_retail_price) VALUES ('" + str(
                                    pr_id) + "','" + str(self.quantity_txt.text()) + "','" + str(
                                    id_of_current_transaction) + "','" + str(pr_wsp) + "','" + str(pr_rp) + "')")
                            stock = pr_lis - int(self.quantity_txt.text())
                            cursor.execute("update product set left_in_stock = '"+str(stock)+"' where id = '"+str(pr_id)+"'")
                        else:
                            cursor.execute(
                                "INSERT INTO pr_in_transaction (product_id,quantity,transaction_id,sold_whole_sale_price,sold_retail_price) VALUES ('" + str(
                                    pr_id) + "','" + str(pr_lis) + "','" + str(
                                    id_of_current_transaction) + "','" + str(pr_wsp) + "','" + str(pr_rp) + "')")
                            cursor.execute(
                               "update product set left_in_stock = '0' where id = '" + str(pr_id) + "'")
                    else:
                        # print("nothing left in stock")
                        self.notification_label.setText('ليس في المخزن')
                        # self.notification_label.setText('No stock left')


                        self.timer = QTimer()
                        self.timer.timeout.connect(self.update_label)
                        self.timer.start(2000)

                cursor.execute("delete from pr_in_transaction where transaction_id ='" + str(id_of_current_transaction) + "' and quantity = 0")
                cursor.execute("select product.name,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity FROM product INNER JOIN pr_in_transaction ON product.id = pr_in_transaction.product_id  where pr_in_transaction.transaction_id ='" + str(
                        id_of_current_transaction) + "'")
                res1 = cursor.fetchall()
                displaying_cursor_in_table(self, res1, self.scanned_table)
                self.quantity_txt.setText("1")
                self.code_txtview.setText("")
                self.calculate_total(res1)

    def update2(self,data):
        self.choice_list_2.clear()
        i = 0
        if isinstance(data, tuple) :
            while i < len(data):
                self.choice_list_2.insertItem(i, str(data[i][0]))
                i = i + 1
        else:
            while i < len(data):
                self.choice_list_2.insertItem(i, str(data[i]))
                i = i + 1

    def update(self,data):
        self.choice_list.clear()
        i = 0
        if isinstance(data, tuple) :
            while i < len(data):
                self.choice_list.insertItem(i, str(data[i][0]))
                i = i + 1
        else:
            while i < len(data):
                self.choice_list.insertItem(i, str(data[i]))
                i = i + 1



    def click(self):
        item = self.choice_list.currentItem()
        self.code_txtview.setText(self.choice_list.currentItem().text())
    def click2(self):
        item = self.choice_list_2.currentItem()
        self.code_txtview_2.setText(self.choice_list_2.currentItem().text())


    def display_search(self):
        cursor = conn.cursor()
        the_before_time_textbox = self.before_timedate_edit.text()
        the_after_time_textbox = self.after_timedate_edit.text()

        the_before_time_textbox = self.before_timedate_edit.text().split(" ", 1)
        the_after_time_textbox = self.after_timedate_edit.text().split(" ", 1)
        before_time = timeConversion(the_before_time_textbox[1])
        after_time = timeConversion(the_after_time_textbox[1])
        the_before_date = datetime.strptime(the_before_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        the_after_date = datetime.strptime(the_after_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        before = the_before_date + " " + before_time + ":00"
        after = the_after_date + " " + after_time + ":00"
        query = "select product.name,pr_in_transaction.sold_whole_sale_price,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity,transactions.date_and_time from product inner join pr_in_transaction on product.id = pr_in_transaction.product_id inner JOIN transactions on transactions.id = pr_in_transaction.transaction_id where transactions.date_and_time >= '" + before + "'and transactions.date_and_time <= '" + after + "'ORDER BY transactions.date_and_time ASC"
        cursor.execute(query)
        result = cursor.fetchall()
        displaying_cursor_in_table(self, result,self.product_display_table)

    def display_all(self):
        cursor = conn.cursor()
        cursor.execute("select product.name,pr_in_transaction.sold_whole_sale_price,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity,transactions.date_and_time from product inner join pr_in_transaction on product.id = pr_in_transaction.product_id inner JOIN transactions on transactions.id = pr_in_transaction.transaction_id ORDER BY transactions.date_and_time ASC")
        res = cursor.fetchall()
        displaying_cursor_in_table(self,res,self.product_display_table)

    def infinit_loop_new(self):
        global bruh
        global id_of_current_transaction
        global id_of_current_customer
        global res1
        self.cancel_btn.setEnabled(1)
        self.validate_btn.setEnabled(1)
        # self.add_btn.setEnabled(1)
        if(bruh == 0):
            conn.rollback()
            self.total_label.setText("0")
            self.scanned_table.setRowCount(0)
        bruh=0
        cursor = conn.cursor()
        ###################
        cursor.execute("select id from customer where name = '"+str(self.customer_name_choice.currentText())+"'")
        id_of_current_customer = cursor.fetchall()[0][0]

        query = "INSERT INTO `transactions`(customer_id) VALUES('"+str(id_of_current_customer)+"')"
        cursor.execute(query)
        cursor.execute("SELECT id FROM `transactions` ORDER BY ID DESC LIMIT 1")
        res = cursor.fetchall()
        id_of_current_transaction = res[0][0]
        ###################
        self.start_btn.setEnabled(0)
        self.customer_name_choice.setEnabled(0)

    def add_custom_item(self):
        global id_of_current_transaction
        global res1
        cursor = conn.cursor()
        if (len(str(self.custom_price_txt.text())) > 0):
            cursor.execute("INSERT INTO PR_IN_TRANSACTION (product_id,quantity,transaction_id,sold_whole_sale_price,sold_retail_price) VALUES ('1','1','" + str(id_of_current_transaction) + "','"+str(self.custom_price_txt.text())+"','"+str(self.custom_price_txt.text())+"')")
            cursor.execute("select product.name,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity FROM product JOIN pr_in_transaction ON product.id = pr_in_transaction.product_id  where pr_in_transaction.transaction_id ='" + str(id_of_current_transaction) + "'")
            res1 = cursor.fetchall()
            displaying_cursor_in_table(self, res1, self.scanned_table)
            self.custom_price_txt.setText("")
            self.calculate_total(res1)

    def insert_product(self):
        cursor = conn.cursor()
        if(len(str(self.pr_name_txt_edit.text()))>0  and len(str(self.pr_re_price_txt_edit.text()))>0 and len(str(self.pr_wh_price_txt_edit.text()))>0):
            if (cursor.execute("select * from product where name ='" + str(self.pr_name_txt_edit.text()) + "'") >= 1):
                cursor.execute("UPDATE `product` SET whole_sale_price = '"+str(self.pr_wh_price_txt_edit.text())+"',retail_price = '" + str(
                    self.pr_re_price_txt_edit.text()) + "' WHERE product.name ='" + str(
                    self.pr_name_txt_edit.text()) + "'")
            else:
                query = "insert into product (name,whole_sale_price,retail_price) values ('" + str(
                    self.pr_name_txt_edit.text()) + "','" + str(
                    self.pr_wh_price_txt_edit.text()) + "','" + str(self.pr_re_price_txt_edit.text()) + "')"
                cursor.execute(query)
            self.pr_name_txt_edit.setText("")
            self.pr_re_price_txt_edit.setText("")
            self.pr_wh_price_txt_edit.setText("")
            self.refresh()
            cursor.execute("select name from product")
            all_prd = cursor.fetchall()
            self.update(all_prd)
            self.update2(all_prd)

        else:
            self.show_message_box("Error","Some fields are empty")
        conn.commit()

    def clackers(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setText('to select click "show details"')
        msgbox.setDetailedText('line 1\nline 2\nline 3')
        msgbox.exec()

    def show_message_box(self,window_title,window_text):
        msg = QMessageBox()
        msg.setWindowTitle(window_title)
        msg.setText(window_text)
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()

    def delete_product(self):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM `product` WHERE product.name = '"+str(self.pr_name_txt_edit.text())+"'")
        conn.commit()
        self.pr_name_txt_edit.setText("")
        self.pr_re_price_txt_edit.setText("")
        self.pr_wh_price_txt_edit.setText("")
        self.refresh()
        cursor.execute("select name from product")
        all_prd = cursor.fetchall()
        self.update(all_prd)
        self.update2(all_prd)

    def calculate_total(self,res):
        price = 0
        for x in res:
            price += x[1] * x[2]
        self.total_label.setText(str(price))

    def calculate_benefit(self,res):
        ben = 0
        cursor = conn.cursor()
        the_before_time_textbox = self.before_timedate_edit.text()
        the_after_time_textbox = self.after_timedate_edit.text()

        the_before_time_textbox = self.before_timedate_edit.text().split(" ", 1)
        the_after_time_textbox = self.after_timedate_edit.text().split(" ", 1)
        before_time = timeConversion(the_before_time_textbox[1])
        after_time = timeConversion(the_after_time_textbox[1])
        the_before_date = datetime.strptime(the_before_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        the_after_date = datetime.strptime(the_after_time_textbox[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        before = the_before_date + " " + before_time + ":00"
        after = the_after_date + " " + after_time + ":00"
        query = "select pr_in_transaction.sold_whole_sale_price,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity from pr_in_transaction inner JOIN transactions on transactions.id = pr_in_transaction.transaction_id where transactions.date_and_time >= '" + before + "'and transactions.date_and_time <= '" + after + "'ORDER BY transactions.date_and_time ASC"
        cursor.execute(query)
        res = cursor.fetchall()
        for x in res:
            ben += (x[1]-x[0]) * x[2]
        textt = "benefit = "+str(ben)
        self.benefit_label.setText(textt)
    def refresh(self):
        cursor = conn.cursor()
        cursor.execute("select name,whole_sale_price,retail_price,left_in_stock from product")
        result = cursor.fetchall()
        displaying_cursor_in_table(self,result,self.pr_table)




    def validate(self):
        global bruh
        cursor = conn.cursor()
        cursor.execute("select debt from customer where id ='"+str(id_of_current_customer)+"'")
        debt = cursor.fetchall()[0][0]
        total = debt + int(self.total_label.text())
        cursor.execute("update customer set debt = '"+str(total)+"' where id = "+str(id_of_current_customer))
        cursor.execute("insert into customer_debt_history (customer_id,debt) values ('"+str(id_of_current_customer)+"','"+str(total)+"')")
        bruh = 1
        self.start_btn.setEnabled(1)
        self.customer_name_choice.setEnabled(1)

        self.scanned_table.setRowCount(0)
        self.cancel_btn.setEnabled(0)
        self.validate_btn.setEnabled(0)
        # self.add_btn.setEnabled(0)
        #################################################
        cursor.execute("select product.name,pr_in_transaction.sold_retail_price,pr_in_transaction.quantity FROM product JOIN pr_in_transaction ON product.id = pr_in_transaction.product_id  where pr_in_transaction.transaction_id ='" + str(id_of_current_transaction) + "'")
        reee = cursor.fetchall()
        workbook = xlsxwriter.Workbook("Les bons\ "+str(datetime.now()).replace(":","-")[:19]+'.xlsx')
        full_border = workbook.add_format(
            {
                "border" :1,
                "border_color": '#000000',
                'font_size': "16"
            }
        )
        no_border = workbook.add_format(
            {
                'font_size': "16"
            }
        )
        worksheet = workbook.add_worksheet()
        worksheet.set_column(2,2,60)
        worksheet.set_column(1,1,14)
        worksheet.write(0,2,"الزبون: "+str(self.customer_name_choice.currentText()), no_border)
        cursor.execute("select date_and_time from transactions where id='"+str(id_of_current_transaction)+"'")
        worksheet.write(1,2,"التاريخ: "+str(cursor.fetchall()[0][0]), no_border)

        col = 3

        i = 0
        worksheet.write(2, 2,"المنتج", full_border)
        worksheet.write(2, 1, "السعر", full_border)
        worksheet.write(2, 0, "الكمية", full_border)
        while(i < len(reee)):
            worksheet.write(col,2,reee[i][0],full_border)
            worksheet.write(col, 1, reee[i][1],full_border)
            worksheet.write(col, 0, reee[i][2],full_border)
            col = col + 1
            i = i + 1
        worksheet.write(col,2,"المجموع: "+str(self.total_label.text()),no_border)
        col = col + 1
        worksheet.write(col,2,'الحساب القديم: '+str(total),no_border)
        col = col + 1

        if self.custom_price_txt.text() != '' and int(self.custom_price_txt.text()) > 0:
            versement = self.custom_price_txt.text()
            cursor = conn.cursor()
            cursor.execute("select debt,id from customer where name = '" + str(
                self.customer_name_choice.currentText()) + "'")
            old_debt = cursor.fetchall()
            debt = old_debt[0][0] - int(self.custom_price_txt.text())
            if debt > 0:
                cursor.execute("update customer set debt = '" + str(debt) + "' where name = '" + str(
                    self.customer_name_choice.currentText()) + "'")
                cursor.execute(
                    "insert into customer_debt_history (customer_id,debt) values ('" + str(
                        old_debt[0][1]) + "','" + str(
                        debt) + "')")
                conn.commit()
                self.show_message_box("success", "Versement à succès")
                self.custom_price_txt.setText('')

        else:
            self.custom_price_txt.setText('')
            versement = '0'

        worksheet.write(col,2,'الدفع: '+ versement,no_border)
        col = col + 1

        cursor.execute("select debt from customer where name = '"+self.customer_name_choice.currentText()+"'")
        new_s = cursor.fetchall()[0][0]
        worksheet.write(col,2,'الحساب الجديد: '+ str(new_s),no_border)
        # for item in content:
        #     worksheet.write(row, column, item)
        #     row += 1
        workbook.close()
        self.total_label.setText("0")
        conn.commit()

        # os.startfile('bon.xlsx', 'print')
        #################################################

    def cancel(self):
        global bruh
        bruh = 1
        conn.rollback()
        self.start_btn.setEnabled(1)
        self.customer_name_choice.setEnabled(1)
        self.total_label.setText("0")
        self.scanned_table.setRowCount(0)
        self.cancel_btn.setEnabled(0)
        self.validate_btn.setEnabled(0)
        # self.add_btn.setEnabled(0)