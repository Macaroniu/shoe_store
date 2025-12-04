# Don't touch this shit!!!! Just close your laptop and go home, trust me u don't want to read it...

import os
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import requests
from PIL import Image

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

COLORS = {
    "primary_bg": "#FFFFFF",
    "secondary_bg": "#7FFF00",
    "accent": "#00FA9A",
    "discount_bg": "#2E8B57",
    "out_of_stock_bg": "#00FA9A",
    "text": "#000000",
    "text_gray": "#666666",
    "button_hover": "#00D080",
    "border": "#CCCCCC",
    "error": "#FF0000",
}


class ShoeShopApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("ООО «Обувь» - Магазин обуви")
        self.geometry("1400x900")
        self.minsize(1200, 700)

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")

        self.setup_icon()

        self.current_user = None
        self.access_token = None

        self.products_cache = []
        self.orders_cache = []
        self.suppliers_cache = []
        self.pickup_points_cache = []

        self.show_login_screen()

    def setup_icon(self):
        try:
            icon_path = Path("static/logo.ico")
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except:
            pass

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        self.clear_window()

        main_frame = ctk.CTkFrame(self, fg_color=COLORS["primary_bg"])
        main_frame.pack(expand=True, fill="both")

        login_frame = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS["primary_bg"],
            border_width=3,
            border_color=COLORS["secondary_bg"],
            corner_radius=10,
        )
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame = ctk.CTkFrame(login_frame, fg_color=COLORS["primary_bg"])
        content_frame.pack(padx=40, pady=40)

        try:
            logo_response = requests.get(f"{API_BASE_URL}/static/images/logo.png", timeout=2)
            if logo_response.status_code == 200:
                logo_image = Image.open(BytesIO(logo_response.content))
                logo_image = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, size=(120, 120))

                logo_label = ctk.CTkLabel(content_frame, image=logo_photo, text="")
                logo_label.pack(pady=(0, 20))
        except:
            pass

        title_label = ctk.CTkLabel(
            content_frame, text="ООО «Обувь»", font=("Times New Roman", 36, "bold"), text_color=COLORS["text"]
        )
        title_label.pack(pady=(0, 5))

        subtitle_label = ctk.CTkLabel(
            content_frame,
            text="Войдите в систему для продолжения",
            font=("Times New Roman", 14),
            text_color=COLORS["text_gray"],
        )
        subtitle_label.pack(pady=(0, 30))

        form_frame = ctk.CTkFrame(content_frame, fg_color=COLORS["primary_bg"])
        form_frame.pack()

        login_label = ctk.CTkLabel(
            form_frame, text="Логин", font=("Times New Roman", 14, "bold"), text_color=COLORS["text"], anchor="w"
        )
        login_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.login_entry = ctk.CTkEntry(
            form_frame,
            width=350,
            height=40,
            font=("Times New Roman", 14),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
        )
        self.login_entry.grid(row=1, column=0, pady=(0, 15))

        password_label = ctk.CTkLabel(
            form_frame, text="Пароль", font=("Times New Roman", 14, "bold"), text_color=COLORS["text"], anchor="w"
        )
        password_label.grid(row=2, column=0, sticky="w", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            form_frame,
            width=350,
            height=40,
            show="*",
            font=("Times New Roman", 14),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
        )
        self.password_entry.grid(row=3, column=0, pady=(0, 20))

        login_button = ctk.CTkButton(
            form_frame,
            text="Войти",
            width=350,
            height=45,
            font=("Times New Roman", 16, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
            command=self.perform_login,
        )
        login_button.grid(row=4, column=0, pady=(0, 10))

        guest_button = ctk.CTkButton(
            form_frame,
            text="Продолжить как гость",
            width=350,
            height=45,
            font=("Times New Roman", 14),
            fg_color=COLORS["primary_bg"],
            hover_color=COLORS["secondary_bg"],
            text_color=COLORS["text"],
            border_width=2,
            border_color=COLORS["secondary_bg"],
            corner_radius=8,
            command=self.login_as_guest,
        )
        guest_button.grid(row=5, column=0)

        self.password_entry.bind("<Return>", lambda e: self.perform_login())
        self.login_entry.bind("<Return>", lambda e: self.password_entry.focus())

        self.login_entry.focus()

    def perform_login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get()

        if not login or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login-json", json={"login": login, "password": password}, timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.current_user = data["user"]
                self.show_main_screen()
            elif response.status_code == 401:
                messagebox.showerror("Ошибка входа", "Неверный логин или пароль")
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror(
                "Ошибка подключения",
                f"Не удалось подключиться к серверу\n\n"
                f"Убедитесь, что FastAPI backend запущен по адресу:\n{API_BASE_URL}",
            )
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def login_as_guest(self):
        self.current_user = {"role": "Гость", "full_name": "Гость", "login": "guest"}
        self.access_token = None
        self.show_main_screen()

    def show_main_screen(self):
        self.clear_window()

        header_frame = ctk.CTkFrame(
            self, height=80, fg_color=COLORS["primary_bg"], border_width=0, border_color=COLORS["secondary_bg"]
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        header_border = ctk.CTkFrame(self, height=3, fg_color=COLORS["secondary_bg"])
        header_border.pack(fill="x")

        left_frame = ctk.CTkFrame(header_frame, fg_color=COLORS["primary_bg"])
        left_frame.pack(side="left", fill="y", padx=20)

        try:
            logo_response = requests.get(f"{API_BASE_URL}/static/images/logo.png", timeout=2)
            if logo_response.status_code == 200:
                logo_image = Image.open(BytesIO(logo_response.content))
                logo_image = logo_image.resize((50, 50), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, size=(50, 50))

                logo_label = ctk.CTkLabel(left_frame, image=logo_photo, text="")
                logo_label.pack(side="left", padx=(0, 15))
        except:
            pass

        title = ctk.CTkLabel(
            left_frame, text="ООО «Обувь»", font=("Times New Roman", 24, "bold"), text_color=COLORS["text"]
        )
        title.pack(side="left", padx=(0, 30))

        nav_frame = ctk.CTkFrame(left_frame, fg_color=COLORS["primary_bg"])
        nav_frame.pack(side="left")

        self.products_nav_btn = ctk.CTkButton(
            nav_frame,
            text="🛍️ Товары",
            font=("Times New Roman", 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
            command=self.show_products_screen,
        )
        self.products_nav_btn.pack(side="left", padx=5)

        if self.current_user["role"] in ["Менеджер", "Администратор"]:
            self.orders_nav_btn = ctk.CTkButton(
                nav_frame,
                text="📦 Заказы",
                font=("Times New Roman", 14, "bold"),
                fg_color=COLORS["primary_bg"],
                hover_color=COLORS["secondary_bg"],
                text_color=COLORS["text"],
                border_width=2,
                border_color=COLORS["secondary_bg"],
                corner_radius=8,
                command=self.show_orders_screen,
            )
            self.orders_nav_btn.pack(side="left", padx=5)

        right_frame = ctk.CTkFrame(header_frame, fg_color=COLORS["primary_bg"])
        right_frame.pack(side="right", fill="y", padx=20)

        user_frame = ctk.CTkFrame(right_frame, fg_color=COLORS["primary_bg"])
        user_frame.pack(side="left", padx=(0, 15))

        user_name = ctk.CTkLabel(
            user_frame,
            text=self.current_user["full_name"],
            font=("Times New Roman", 14, "bold"),
            text_color=COLORS["text"],
            anchor="e",
        )
        user_name.pack(anchor="e")

        logout_btn = ctk.CTkButton(
            right_frame,
            text="Выход",
            width=100,
            font=("Times New Roman", 14, "bold"),
            fg_color=COLORS["discount_bg"],
            hover_color="#246B43",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.logout,
        )
        logout_btn.pack(side="left")

        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["primary_bg"])
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.show_products_screen()

    def logout(self):
        self.current_user = None
        self.access_token = None
        self.products_cache = []
        self.orders_cache = []
        self.show_login_screen()

    def show_products_screen(self):
        self.products_nav_btn.configure(fg_color=COLORS["accent"], border_width=0)
        if hasattr(self, "orders_nav_btn"):
            self.orders_nav_btn.configure(fg_color=COLORS["primary_bg"], border_width=2)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        main_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["primary_bg"])
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        header_container = ctk.CTkFrame(main_container, fg_color=COLORS["primary_bg"])
        header_container.pack(fill="x", pady=(0, 20))

        title_frame = ctk.CTkFrame(header_container, fg_color=COLORS["primary_bg"])
        title_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_frame, text="Каталог товаров", font=("Times New Roman", 32, "bold"), text_color=COLORS["text"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Выберите подходящую пару обуви",
            font=("Times New Roman", 14),
            text_color=COLORS["text_gray"],
        )
        subtitle.pack(anchor="w")

        if self.current_user["role"] == "Администратор":
            add_btn = ctk.CTkButton(
                header_container,
                text="➕ Добавить товар",
                font=("Times New Roman", 14, "bold"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["button_hover"],
                text_color=COLORS["text"],
                corner_radius=8,
                command=self.add_product,
            )
            add_btn.pack(side="right")

        header_border = ctk.CTkFrame(main_container, height=3, fg_color=COLORS["secondary_bg"])
        header_border.pack(fill="x", pady=(0, 20))

        if self.current_user["role"] in ["Менеджер", "Администратор"]:
            filter_container = ctk.CTkFrame(
                main_container,
                fg_color=COLORS["primary_bg"],
                border_width=3,
                border_color=COLORS["secondary_bg"],
                corner_radius=8,
            )
            filter_container.pack(fill="x", pady=(0, 20))

            filter_inner = ctk.CTkFrame(filter_container, fg_color=COLORS["primary_bg"])
            filter_inner.pack(fill="x", padx=20, pady=20)

            filter_inner.grid_columnconfigure(0, weight=2)
            filter_inner.grid_columnconfigure(1, weight=1)
            filter_inner.grid_columnconfigure(2, weight=1)

            search_frame = ctk.CTkFrame(filter_inner, fg_color=COLORS["primary_bg"])
            search_frame.grid(row=0, column=0, padx=(0, 15), sticky="ew")

            search_label = ctk.CTkLabel(
                search_frame, text="🔍 Поиск", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"]
            )
            search_label.pack(anchor="w", pady=(0, 5))

            self.search_entry = ctk.CTkEntry(
                search_frame,
                placeholder_text="Артикул, название, описание...",
                font=("Times New Roman", 12),
                border_width=2,
                border_color=COLORS["secondary_bg"],
                fg_color=COLORS["primary_bg"],
            )
            self.search_entry.pack(fill="x")
            self.search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

            supplier_frame = ctk.CTkFrame(filter_inner, fg_color=COLORS["primary_bg"])
            supplier_frame.grid(row=0, column=1, padx=(0, 15), sticky="ew")

            supplier_label = ctk.CTkLabel(
                supplier_frame, text="🏢 Поставщик", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"]
            )
            supplier_label.pack(anchor="w", pady=(0, 5))

            self.supplier_var = ctk.StringVar(value="Все поставщики")
            self.supplier_combo = ctk.CTkComboBox(
                supplier_frame,
                variable=self.supplier_var,
                values=["Все поставщики"],
                font=("Times New Roman", 12),
                border_width=2,
                border_color=COLORS["secondary_bg"],
                fg_color=COLORS["primary_bg"],
                button_color=COLORS["secondary_bg"],
                button_hover_color=COLORS["accent"],
                command=lambda _: self.apply_filters(),
            )
            self.supplier_combo.pack(fill="x")

            sort_frame = ctk.CTkFrame(filter_inner, fg_color=COLORS["primary_bg"])
            sort_frame.grid(row=0, column=2, sticky="ew")

            sort_label = ctk.CTkLabel(
                sort_frame, text="📊 Сортировка", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"]
            )
            sort_label.pack(anchor="w", pady=(0, 5))

            self.sort_var = ctk.StringVar(value="По умолчанию")
            sort_combo = ctk.CTkComboBox(
                sort_frame,
                variable=self.sort_var,
                values=["По умолчанию", "Количество ↑", "Количество ↓"],
                font=("Times New Roman", 12),
                border_width=2,
                border_color=COLORS["secondary_bg"],
                fg_color=COLORS["primary_bg"],
                button_color=COLORS["secondary_bg"],
                button_hover_color=COLORS["accent"],
                command=lambda _: self.apply_filters(),
            )
            sort_combo.pack(fill="x")

        self.products_scroll = ctk.CTkScrollableFrame(main_container, fg_color=COLORS["primary_bg"], border_width=0)
        self.products_scroll.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.load_products()

    def apply_filters(self):
        self.load_products()

    def load_products(self):
        for widget in self.products_scroll.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.products_scroll,
            text="⏳ Загрузка товаров...",
            font=("Times New Roman", 16),
            text_color=COLORS["text_gray"],
        )
        loading_label.pack(pady=50)

        self.update()

        params = {}

        if self.current_user["role"] in ["Менеджер", "Администратор"]:
            if hasattr(self, "search_entry"):
                search = self.search_entry.get().strip()
                if search:
                    params["search"] = search

            if hasattr(self, "supplier_var"):
                supplier = self.supplier_var.get()
                if supplier and supplier != "Все поставщики":
                    params["supplier"] = supplier

            if hasattr(self, "sort_var"):
                sort_option = self.sort_var.get()
                if sort_option == "Количество ↑":
                    params["sort_by_quantity"] = "asc"
                elif sort_option == "Количество ↓":
                    params["sort_by_quantity"] = "desc"

        try:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"

            response = requests.get(f"{API_BASE_URL}/api/products", params=params, headers=headers, timeout=5)

            if response.status_code == 200:
                self.products_cache = response.json()

                if self.current_user["role"] == "Администратор":
                    self.load_suppliers()

                loading_label.destroy()

                if self.products_cache:
                    self.display_products()
                else:
                    no_data = ctk.CTkLabel(
                        self.products_scroll,
                        text="Товары не найдены",
                        font=("Times New Roman", 16),
                        text_color=COLORS["text_gray"],
                    )
                    no_data.pack(pady=50)
            else:
                loading_label.destroy()
                error_label = ctk.CTkLabel(
                    self.products_scroll,
                    text=f"❌ Ошибка загрузки товаров: {response.status_code}",
                    font=("Times New Roman", 14),
                    text_color=COLORS["error"],
                )
                error_label.pack(pady=50)
        except Exception as e:
            loading_label.destroy()
            error_label = ctk.CTkLabel(
                self.products_scroll,
                text=f"❌ Не удалось загрузить товары:\n{str(e)}",
                font=("Times New Roman", 14),
                text_color=COLORS["error"],
            )
            error_label.pack(pady=50)

    def load_suppliers(self):
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{API_BASE_URL}/api/products/suppliers", headers=headers, timeout=5)

            if response.status_code == 200:
                self.suppliers_cache = response.json()
                if hasattr(self, "supplier_combo"):
                    self.supplier_combo.configure(values=self.suppliers_cache)
        except Exception as e:
            print(f"Ошибка загрузки поставщиков: {e}")

    def display_products(self):
        for product in self.products_cache:
            self.create_product_card(product)

    def create_product_card(self, product):

        if product["quantity"] == 0 or product.get("out_of_stock", False):
            card_bg = COLORS["out_of_stock_bg"]
            border_color = COLORS["out_of_stock_bg"]
            image_bg = COLORS["out_of_stock_bg"]
        elif product["discount"] > 15:
            card_bg = COLORS["discount_bg"]
            border_color = COLORS["discount_bg"]
            image_bg = COLORS["discount_bg"]
        else:
            card_bg = COLORS["primary_bg"]
            border_color = COLORS["secondary_bg"]
            image_bg = COLORS["secondary_bg"]

        card_outer = ctk.CTkFrame(self.products_scroll, fg_color="transparent")
        card_outer.pack(fill="x", padx=10, pady=10)

        card = ctk.CTkFrame(card_outer, fg_color=card_bg, border_width=3, border_color=border_color, corner_radius=8)
        card.pack(fill="x")

        if self.current_user["role"] == "Администратор":
            card.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
            card.configure(cursor="hand2")

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        if self.current_user["role"] == "Администратор":
            content_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        image_frame = ctk.CTkFrame(content_frame, width=220, fg_color=image_bg, corner_radius=0)
        image_frame.pack(side="left", fill="y", padx=0, pady=0)
        image_frame.pack_propagate(False)

        if self.current_user["role"] == "Администратор":
            image_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        try:
            if product.get("photo"):
                img_url = f"{API_BASE_URL}{product['photo']}"
                img_response = requests.get(img_url, timeout=2)
                if img_response.status_code == 200:
                    img = Image.open(BytesIO(img_response.content))
                    img = img.resize((200, 180), Image.Resampling.LANCZOS)
                    photo = ctk.CTkImage(light_image=img, size=(200, 180))

                    img_label = ctk.CTkLabel(image_frame, image=photo, text="")
                    img_label.place(relx=0.5, rely=0.5, anchor="center")

                    if self.current_user["role"] == "Администратор":
                        img_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))
                else:
                    raise Exception()
            else:
                raise Exception()
        except:
            placeholder = ctk.CTkLabel(image_frame, text="👞", font=("Times New Roman", 72), text_color=COLORS["text"])
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
            if self.current_user["role"] == "Администратор":
                placeholder.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        if self.current_user["role"] == "Администратор":
            info_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        top_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 8))

        if self.current_user["role"] == "Администратор":
            top_row.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        article_label = ctk.CTkLabel(
            top_row,
            text=f"Артикул: {product['article']}",
            font=("Times New Roman", 14, "bold"),
            text_color=COLORS["text"],
        )
        article_label.pack(side="left")

        if self.current_user["role"] == "Администратор":
            article_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        if product["discount"] > 0:
            discount_label = ctk.CTkLabel(
                top_row,
                text=f"-{product['discount']}%",
                font=("Times New Roman", 13, "bold"),
                text_color="#FFFFFF",
                fg_color=COLORS["discount_bg"],
                corner_radius=15,
                padx=12,
                pady=4,
            )
            discount_label.pack(side="right")
            if self.current_user["role"] == "Администратор":
                discount_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        name_label = ctk.CTkLabel(
            info_frame,
            text=product["name"],
            font=("Times New Roman", 18, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        name_label.pack(fill="x", pady=(0, 8))
        if self.current_user["role"] == "Администратор":
            name_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        if product.get("description"):
            desc_text = product["description"][:120] + ("..." if len(product["description"]) > 120 else "")
            desc_label = ctk.CTkLabel(
                info_frame,
                text=desc_text,
                font=("Times New Roman", 12),
                text_color=COLORS["text_gray"],
                anchor="w",
                wraplength=700,
            )
            desc_label.pack(fill="x", pady=(0, 12))
            if self.current_user["role"] == "Администратор":
                desc_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill="x", pady=(0, 12))
        details_frame.grid_columnconfigure((0, 1, 2), weight=1)

        if self.current_user["role"] == "Администратор":
            details_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        self._create_info_field(details_frame, "Категория", product["category"], 0, 0, product)
        self._create_info_field(details_frame, "Производитель", product["manufacturer"], 0, 1, product)
        self._create_info_field(details_frame, "Поставщик", product["supplier"], 0, 2, product)

        separator = ctk.CTkFrame(info_frame, height=2, fg_color=COLORS["secondary_bg"])
        separator.pack(fill="x", pady=(0, 12))
        if self.current_user["role"] == "Администратор":
            separator.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        bottom_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        bottom_row.pack(fill="x")
        if self.current_user["role"] == "Администратор":
            bottom_row.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        price_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
        price_frame.pack(side="left")
        if self.current_user["role"] == "Администратор":
            price_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        if product["discount"] > 0:
            original_price = ctk.CTkLabel(
                price_frame,
                text=f"{product['price']:.2f} ₽",
                font=("Times New Roman", 12, "overstrike"),
                text_color=COLORS["error"],
            )
            original_price.pack()
            if self.current_user["role"] == "Администратор":
                original_price.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        final_price = ctk.CTkLabel(
            price_frame,
            text=f"{product['final_price']:.2f} ₽",
            font=("Times New Roman", 22, "bold"),
            text_color=COLORS["text"],
        )
        final_price.pack()
        if self.current_user["role"] == "Администратор":
            final_price.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        if product.get("out_of_stock", False) or product["quantity"] == 0:
            stock_text = "НЕТ В НАЛИЧИИ"
            stock_color = COLORS["error"]
        elif product["quantity"] <= 3:
            stock_text = f"Осталось {product['quantity']} {product['unit']}"
            stock_color = "#FFA500"
        else:
            stock_text = f"В наличии: {product['quantity']} {product['unit']}"
            stock_color = COLORS["discount_bg"]

        stock_label = ctk.CTkLabel(
            bottom_row, text=stock_text, font=("Times New Roman", 13, "bold"), text_color=stock_color
        )
        stock_label.pack(side="right")
        if self.current_user["role"] == "Администратор":
            stock_label.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        if self.current_user["role"] == "Администратор":
            separator2 = ctk.CTkFrame(card, height=2, fg_color=COLORS["secondary_bg"])
            separator2.pack(fill="x")

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=12)

            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Удалить",
                width=140,
                font=("Times New Roman", 12, "bold"),
                fg_color=COLORS["discount_bg"],
                hover_color="#246B43",
                text_color="#FFFFFF",
                corner_radius=6,
                command=lambda p=product: self.delete_product(p),
            )
            delete_btn.pack(side="left")

    def _create_info_field(self, parent, label, value, row, col, product=None):
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.grid(row=row, column=col, sticky="w", padx=(0, 15), pady=5)

        if self.current_user["role"] == "Администратор" and product:
            field_frame.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        label_widget = ctk.CTkLabel(
            field_frame, text=label.upper(), font=("Times New Roman", 10, "bold"), text_color=COLORS["text_gray"]
        )
        label_widget.pack(anchor="w")

        if self.current_user["role"] == "Администратор" and product:
            label_widget.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

        value_widget = ctk.CTkLabel(
            field_frame, text=value, font=("Times New Roman", 13, "bold"), text_color=COLORS["text"]
        )
        value_widget.pack(anchor="w")

        if self.current_user["role"] == "Администратор" and product:
            value_widget.bind("<Button-1>", lambda e, p=product: self.edit_product(p))

    def add_product(self):
        ProductDialog(self, mode="add")

    def edit_product(self, product):
        ProductDialog(self, mode="edit", product=product)

    def delete_product(self, product):
        if messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить товар?\n\n"
            f"Артикул: {product['article']}\n"
            f"Название: {product['name']}",
        ):
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.delete(
                    f"{API_BASE_URL}/api/products/{product['article']}", headers=headers, timeout=5
                )

                if response.status_code == 204:
                    messagebox.showinfo("Успех", "Товар успешно удален")
                    self.load_products()
                elif response.status_code == 400:
                    messagebox.showerror("Ошибка удаления", "Невозможно удалить товар, который присутствует в заказах")
                else:
                    messagebox.showerror("Ошибка", f"Ошибка удаления: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить товар:\n{str(e)}")

    def show_orders_screen(self):
        self.products_nav_btn.configure(fg_color=COLORS["primary_bg"], border_width=2)
        self.orders_nav_btn.configure(fg_color=COLORS["accent"], border_width=0)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        main_container = ctk.CTkFrame(self.content_frame, fg_color=COLORS["primary_bg"])
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        header_container = ctk.CTkFrame(main_container, fg_color=COLORS["primary_bg"])
        header_container.pack(fill="x", pady=(0, 20))

        title_frame = ctk.CTkFrame(header_container, fg_color=COLORS["primary_bg"])
        title_frame.pack(side="left")

        title = ctk.CTkLabel(
            title_frame, text="Управление заказами", font=("Times New Roman", 32, "bold"), text_color=COLORS["text"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Просмотр и обработка заказов",
            font=("Times New Roman", 14),
            text_color=COLORS["text_gray"],
        )
        subtitle.pack(anchor="w")

        if self.current_user["role"] == "Администратор":
            add_btn = ctk.CTkButton(
                header_container,
                text="➕ Создать заказ",
                font=("Times New Roman", 14, "bold"),
                fg_color=COLORS["accent"],
                hover_color=COLORS["button_hover"],
                text_color=COLORS["text"],
                corner_radius=8,
                command=self.add_order,
            )
            add_btn.pack(side="right")

        header_border = ctk.CTkFrame(main_container, height=3, fg_color=COLORS["secondary_bg"])
        header_border.pack(fill="x", pady=(0, 20))

        self.orders_scroll = ctk.CTkScrollableFrame(main_container, fg_color=COLORS["primary_bg"], border_width=0)
        self.orders_scroll.pack(fill="both", expand=True)

        self.load_orders()

    def load_orders(self):
        for widget in self.orders_scroll.winfo_children():
            widget.destroy()

        loading_label = ctk.CTkLabel(
            self.orders_scroll,
            text="⏳ Загрузка заказов...",
            font=("Times New Roman", 16),
            text_color=COLORS["text_gray"],
        )
        loading_label.pack(pady=50)
        self.update()

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(f"{API_BASE_URL}/api/orders", headers=headers, timeout=5)

            if response.status_code == 200:
                self.orders_cache = response.json()
                loading_label.destroy()

                if self.orders_cache:
                    self.display_orders()
                else:
                    ctk.CTkLabel(
                        self.orders_scroll,
                        text="Заказы не найдены",
                        font=("Times New Roman", 16),
                        text_color=COLORS["text_gray"],
                    ).pack(pady=50)
            else:
                loading_label.destroy()
                ctk.CTkLabel(
                    self.orders_scroll,
                    text=f"❌ Ошибка загрузки: {response.status_code}",
                    font=("Times New Roman", 14),
                    text_color=COLORS["error"],
                ).pack(pady=50)
        except Exception as e:
            loading_label.destroy()
            ctk.CTkLabel(
                self.orders_scroll,
                text=f"❌ Не удалось загрузить заказы:\n{str(e)}",
                font=("Times New Roman", 14),
                text_color=COLORS["error"],
            ).pack(pady=50)

    def display_orders(self):
        for order in self.orders_cache:
            self.create_order_card(order)

    def create_order_card(self, order):
        if order["status"].lower() in ["новый", "new"]:
            status_bg = COLORS["secondary_bg"]
            status_text = COLORS["text"]
        else:
            status_bg = COLORS["accent"]
            status_text = COLORS["text"]

        card = ctk.CTkFrame(
            self.orders_scroll,
            fg_color=COLORS["primary_bg"],
            border_width=3,
            border_color=COLORS["secondary_bg"],
            corner_radius=8,
        )
        card.pack(fill="x", pady=(0, 15))

        if self.current_user["role"] == "Администратор":
            card.bind("<Button-1>", lambda e, o=order: self.edit_order(o))
            card.configure(cursor="hand2")

        content = ctk.CTkFrame(card, fg_color=COLORS["primary_bg"])
        content.pack(fill="both", padx=20, pady=20)

        if self.current_user["role"] == "Администратор":
            content.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        header_frame = ctk.CTkFrame(content, fg_color=COLORS["primary_bg"])
        header_frame.pack(fill="x", pady=(0, 15))

        if self.current_user["role"] == "Администратор":
            header_frame.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        order_num = ctk.CTkLabel(
            header_frame,
            text=f"Заказ №{order['order_number']}",
            font=("Times New Roman", 22, "bold"),
            text_color=COLORS["text"],
        )
        order_num.pack(side="left")

        if self.current_user["role"] == "Администратор":
            order_num.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        status_label = ctk.CTkLabel(
            header_frame,
            text=order["status"],
            font=("Times New Roman", 13, "bold"),
            text_color=status_text,
            fg_color=status_bg,
            corner_radius=20,
            padx=16,
            pady=6,
        )
        status_label.pack(side="right")

        if self.current_user["role"] == "Администратор":
            status_label.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        separator = ctk.CTkFrame(content, height=2, fg_color=COLORS["secondary_bg"])
        separator.pack(fill="x", pady=(0, 15))

        if self.current_user["role"] == "Администратор":
            separator.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        info_grid = ctk.CTkFrame(content, fg_color=COLORS["primary_bg"])
        info_grid.pack(fill="x", pady=(0, 15))
        info_grid.grid_columnconfigure((0, 1, 2), weight=1)

        if self.current_user["role"] == "Администратор":
            info_grid.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        self._create_info_field(info_grid, "Дата заказа", order["order_date"], 0, 0)
        self._create_info_field(info_grid, "Дата выдачи", order["delivery_date"], 0, 1)
        self._create_info_field(info_grid, "Клиент", order["client_full_name"], 1, 0)
        self._create_info_field(info_grid, "Код получения", str(order["code"]), 1, 1)

        if order.get("pickup_address"):
            address_label = ctk.CTkLabel(
                info_grid, text="ПУНКТ ВЫДАЧИ", font=("Times New Roman", 10, "bold"), text_color=COLORS["text_gray"]
            )
            address_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 2))

            if self.current_user["role"] == "Администратор":
                address_label.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

            address_value = ctk.CTkLabel(
                info_grid, text=order["pickup_address"], font=("Times New Roman", 13, "bold"), text_color=COLORS["text"]
            )
            address_value.grid(row=3, column=0, columnspan=3, sticky="w")

            if self.current_user["role"] == "Администратор":
                address_value.bind("<Button-1>", lambda e, o=order: self.edit_order(o))

        if self.current_user["role"] == "Администратор":
            separator2 = ctk.CTkFrame(content, height=2, fg_color=COLORS["secondary_bg"])
            separator2.pack(fill="x", pady=(15, 0))

            btn_frame = ctk.CTkFrame(content, fg_color=COLORS["primary_bg"])
            btn_frame.pack(fill="x", pady=(15, 0))

            delete_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Удалить",
                width=140,
                font=("Times New Roman", 12, "bold"),
                fg_color=COLORS["discount_bg"],
                hover_color="#246B43",
                text_color="#FFFFFF",
                corner_radius=6,
                command=lambda o=order: self.delete_order(o),
            )
            delete_btn.pack(side="left")

    def add_order(self):
        OrderDialog(self, mode="add")

    def edit_order(self, order):
        OrderDialog(self, mode="edit", order=order)

    def delete_order(self, order):
        if messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить заказ?\n\n"
            f"Номер заказа: {order['order_number']}\n"
            f"Клиент: {order['client_full_name']}",
        ):
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.delete(f"{API_BASE_URL}/api/orders/{order['id']}", headers=headers, timeout=5)

                if response.status_code == 204:
                    messagebox.showinfo("Успех", "Заказ успешно удален")
                    self.load_orders()
                else:
                    messagebox.showerror("Ошибка", f"Ошибка удаления: {response.status_code}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заказ:\n{str(e)}")


class ProductDialog(ctk.CTkToplevel):

    def __init__(self, parent, mode="add", product=None):
        super().__init__(parent)

        self.parent = parent
        self.mode = mode
        self.product = product
        self.selected_image = None

        title_text = "Добавление товара" if mode == "add" else "Редактирование товара"
        self.title(title_text)
        self.geometry("900x750")

        self.transient(parent)
        self.grab_set()

        self.create_widgets()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["secondary_bg"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Добавление товара" if self.mode == "add" else "Редактирование товара",
            font=("Times New Roman", 20, "bold"),
            text_color=COLORS["text"],
        )
        title.pack(side="left", padx=20)

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["primary_bg"])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scroll_frame.grid_columnconfigure((0, 1), weight=1)

        fields = [
            ("Артикул *", "article", "entry", self.mode == "add"),
            ("Наименование *", "name", "entry", True),
            ("Категория *", "category", "combo", True),
            ("Производитель *", "manufacturer", "entry", True),
            ("Поставщик *", "supplier", "entry", True),
            ("Единица измерения *", "unit", "entry", True),
            ("Цена (₽) *", "price", "entry", True),
            ("Скидка (%)", "discount", "entry", True),
            ("Количество на складе *", "quantity", "entry", True),
        ]

        self.entries = {}
        row = 0

        for i, (label_text, field_name, field_type, enabled) in enumerate(fields):
            col = i % 2
            if i % 2 == 0 and i > 0:
                row += 1

            field_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
            field_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

            label = ctk.CTkLabel(
                field_frame,
                text=label_text,
                font=("Times New Roman", 12, "bold"),
                text_color=COLORS["text"],
                anchor="w",
            )
            label.pack(fill="x", pady=(0, 5))

            if field_type == "combo" and field_name == "category":
                categories = ["Женская обувь", "Мужская обувь", "Детская обувь", "Спортивная обувь"]
                entry = ctk.CTkComboBox(
                    field_frame,
                    values=categories,
                    font=("Times New Roman", 12),
                    border_width=2,
                    border_color=COLORS["secondary_bg"],
                    fg_color=COLORS["primary_bg"],
                    button_color=COLORS["secondary_bg"],
                    button_hover_color=COLORS["accent"],
                    state="readonly" if not enabled else "normal",
                )
            else:
                entry = ctk.CTkEntry(
                    field_frame,
                    font=("Times New Roman", 12),
                    border_width=2,
                    border_color=COLORS["secondary_bg"],
                    fg_color=COLORS["primary_bg"],
                    state="normal" if enabled else "disabled",
                )

            entry.pack(fill="x")
            self.entries[field_name] = entry

            if self.mode == "edit" and self.product:
                value = self.product.get(field_name, "")
                if field_type == "combo":
                    entry.set(str(value) if value else categories[0])
                else:
                    entry.insert(0, str(value) if value else "")

        row += 1
        desc_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        desc_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        desc_label = ctk.CTkLabel(
            desc_frame, text="Описание", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"], anchor="w"
        )
        desc_label.pack(fill="x", pady=(0, 5))

        self.description_text = ctk.CTkTextbox(
            desc_frame,
            height=100,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
        )
        self.description_text.pack(fill="x")

        if self.mode == "edit" and self.product:
            desc = self.product.get("description", "")
            if desc:
                self.description_text.insert("1.0", desc)

        row += 1
        image_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        image_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        image_label = ctk.CTkLabel(
            image_frame, text="Изображение", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"], anchor="w"
        )
        image_label.pack(fill="x", pady=(0, 5))

        upload_btn = ctk.CTkButton(
            image_frame,
            text="📁 Выбрать изображение",
            font=("Times New Roman", 12),
            fg_color=COLORS["secondary_bg"],
            hover_color=COLORS["accent"],
            text_color=COLORS["text"],
            command=self.select_image,
        )
        upload_btn.pack()

        footer = ctk.CTkFrame(self, fg_color=COLORS["primary_bg"], height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        separator = ctk.CTkFrame(footer, height=2, fg_color=COLORS["secondary_bg"])
        separator.pack(fill="x")

        btn_frame = ctk.CTkFrame(footer, fg_color=COLORS["primary_bg"])
        btn_frame.pack(expand=True)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Отмена",
            width=120,
            font=("Times New Roman", 14),
            fg_color=COLORS["primary_bg"],
            hover_color=COLORS["secondary_bg"],
            text_color=COLORS["text"],
            border_width=2,
            border_color=COLORS["secondary_bg"],
            corner_radius=8,
            command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            width=150,
            font=("Times New Roman", 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
            command=self.save,
        )
        save_btn.pack(side="left", padx=10)

    def select_image(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение", filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if filename:
            self.selected_image = filename
            messagebox.showinfo("Изображение выбрано", f"Выбран файл:\n{Path(filename).name}")

    def save(self):
        data = {}
        required_fields = ["article", "name", "category", "manufacturer", "supplier", "unit", "price", "quantity"]

        for field_name, entry in self.entries.items():
            if hasattr(entry, "get"):
                value = entry.get().strip()
            else:
                value = entry.get().strip() if hasattr(entry, "get") else ""

            if field_name in required_fields and not value:
                messagebox.showerror("Ошибка", f"Заполните поле: {field_name}")
                return

            if field_name == "price":
                try:
                    value = float(value) if value else 0
                except:
                    messagebox.showerror("Ошибка", "Неверное значение цены")
                    return
            elif field_name in ["discount", "quantity"]:
                try:
                    value = int(value) if value else 0
                except:
                    messagebox.showerror("Ошибка", f"Неверное значение для поля {field_name}")
                    return

            data[field_name] = value

        desc = self.description_text.get("1.0", "end-1c").strip()
        data["description"] = desc if desc else None

        try:
            headers = {"Authorization": f"Bearer {self.parent.access_token}", "Content-Type": "application/json"}

            if self.mode == "add":
                response = requests.post(f"{API_BASE_URL}/api/products", json=data, headers=headers, timeout=5)
            else:
                article = self.product["article"]
                response = requests.put(f"{API_BASE_URL}/api/products/{article}", json=data, headers=headers, timeout=5)

            if response.status_code in [200, 201]:
                product_data = response.json()
                article = product_data.get("article")

                if self.selected_image and article:
                    self.upload_image(article)

                messagebox.showinfo("Успех", "Товар успешно сохранен")
                self.parent.load_products()
                self.destroy()
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Ошибка валидации")
                messagebox.showerror("Ошибка", error_detail)
            else:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить товар:\n{str(e)}")

    def upload_image(self, article):
        try:
            with open(self.selected_image, "rb") as f:
                files = {"file": f}
                headers = {"Authorization": f"Bearer {self.parent.access_token}"}

                response = requests.post(
                    f"{API_BASE_URL}/api/products/{article}/upload-image", files=files, headers=headers, timeout=10
                )

                if response.status_code != 200:
                    messagebox.showwarning("Предупреждение", "Не удалось загрузить изображение")
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Ошибка загрузки изображения: {str(e)}")


class OrderDialog(ctk.CTkToplevel):

    def __init__(self, parent, mode="add", order=None):
        super().__init__(parent)

        self.parent = parent
        self.mode = mode
        self.order = order
        self.order_products = []

        title_text = "Создание заказа" if mode == "add" else "Редактирование заказа"
        self.title(title_text)
        self.geometry("800x700")

        self.transient(parent)
        self.grab_set()

        self.load_pickup_points()
        self.create_widgets()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def load_pickup_points(self):
        try:
            headers = {"Authorization": f"Bearer {self.parent.access_token}"}
            response = requests.get(f"{API_BASE_URL}/api/orders/pickup-points", headers=headers, timeout=5)

            if response.status_code == 200:
                self.parent.pickup_points_cache = response.json()
        except Exception as e:
            print(f"Ошибка загрузки пунктов выдачи: {e}")

    def create_widgets(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["secondary_bg"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="Создание заказа" if self.mode == "add" else "Редактирование заказа",
            font=("Times New Roman", 20, "bold"),
            text_color=COLORS["text"],
        )
        title.pack(side="left", padx=20)

        scroll_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["primary_bg"])
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        scroll_frame.grid_columnconfigure((0, 1), weight=1)

        row = 0

        date_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        date_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        date_label = ctk.CTkLabel(
            date_frame,
            text="Дата заказа *",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        date_label.pack(fill="x", pady=(0, 5))

        self.order_date_entry = ctk.CTkEntry(
            date_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            placeholder_text="ГГГГ-ММ-ДД",
        )
        self.order_date_entry.pack(fill="x")

        if self.mode == "add":
            self.order_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        elif self.order:
            self.order_date_entry.insert(0, self.order["order_date"])

        delivery_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        delivery_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        delivery_label = ctk.CTkLabel(
            delivery_frame,
            text="Дата выдачи *",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        delivery_label.pack(fill="x", pady=(0, 5))

        self.delivery_date_entry = ctk.CTkEntry(
            delivery_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            placeholder_text="ГГГГ-ММ-ДД",
        )
        self.delivery_date_entry.pack(fill="x")

        if self.mode == "add":
            self.delivery_date_entry.insert(0, (date.today() + timedelta(days=3)).strftime("%Y-%m-%d"))
        elif self.order:
            self.delivery_date_entry.insert(0, self.order["delivery_date"])

        row += 1

        client_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        client_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        client_label = ctk.CTkLabel(
            client_frame,
            text="ФИО клиента *",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        client_label.pack(fill="x", pady=(0, 5))

        self.client_entry = ctk.CTkEntry(
            client_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
        )
        self.client_entry.pack(fill="x")

        if self.order:
            self.client_entry.insert(0, self.order["client_full_name"])

        code_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        code_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        code_label = ctk.CTkLabel(
            code_frame,
            text="Код получения *",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        code_label.pack(fill="x", pady=(0, 5))

        self.code_entry = ctk.CTkEntry(
            code_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            placeholder_text="100-9999",
        )
        self.code_entry.pack(fill="x")

        if self.order:
            self.code_entry.insert(0, str(self.order["code"]))

        row += 1

        pickup_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        pickup_frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")

        pickup_label = ctk.CTkLabel(
            pickup_frame,
            text="Пункт выдачи *",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        pickup_label.pack(fill="x", pady=(0, 5))

        pickup_addresses = [p["address"] for p in self.parent.pickup_points_cache]
        self.pickup_var = ctk.StringVar()
        self.pickup_combo = ctk.CTkComboBox(
            pickup_frame,
            variable=self.pickup_var,
            values=pickup_addresses if pickup_addresses else ["Нет пунктов выдачи"],
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            button_color=COLORS["secondary_bg"],
            button_hover_color=COLORS["accent"],
            state="readonly",
        )
        self.pickup_combo.pack(fill="x")

        if pickup_addresses:
            if self.order and self.order.get("pickup_address"):
                self.pickup_var.set(self.order["pickup_address"])
            else:
                self.pickup_var.set(pickup_addresses[0])

        status_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        status_frame.grid(row=row, column=1, padx=10, pady=10, sticky="ew")

        status_label = ctk.CTkLabel(
            status_frame, text="Статус *", font=("Times New Roman", 12, "bold"), text_color=COLORS["text"], anchor="w"
        )
        status_label.pack(fill="x", pady=(0, 5))

        self.status_var = ctk.StringVar(value="Новый")
        status_combo = ctk.CTkComboBox(
            status_frame,
            variable=self.status_var,
            values=["Новый", "Завершен"],
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            button_color=COLORS["secondary_bg"],
            button_hover_color=COLORS["accent"],
            state="readonly",
        )
        status_combo.pack(fill="x")

        if self.order:
            self.status_var.set(self.order["status"])

        row += 1

        products_frame = ctk.CTkFrame(scroll_frame, fg_color=COLORS["primary_bg"])
        products_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        products_label = ctk.CTkLabel(
            products_frame,
            text="Товары в заказе",
            font=("Times New Roman", 12, "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        products_label.pack(fill="x", pady=(0, 10))

        self.products_container = ctk.CTkFrame(products_frame, fg_color=COLORS["primary_bg"])
        self.products_container.pack(fill="x")

        add_product_btn = ctk.CTkButton(
            products_frame,
            text="➕ Добавить товар",
            font=("Times New Roman", 12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            command=self.add_product_row,
        )
        add_product_btn.pack(pady=(10, 0))

        footer = ctk.CTkFrame(self, fg_color=COLORS["primary_bg"], height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        separator = ctk.CTkFrame(footer, height=2, fg_color=COLORS["secondary_bg"])
        separator.pack(fill="x")

        btn_frame = ctk.CTkFrame(footer, fg_color=COLORS["primary_bg"])
        btn_frame.pack(expand=True)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Отмена",
            width=120,
            font=("Times New Roman", 14),
            fg_color=COLORS["primary_bg"],
            hover_color=COLORS["secondary_bg"],
            text_color=COLORS["text"],
            border_width=2,
            border_color=COLORS["secondary_bg"],
            corner_radius=8,
            command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Сохранить",
            width=150,
            font=("Times New Roman", 14, "bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["button_hover"],
            text_color=COLORS["text"],
            corner_radius=8,
            command=self.save,
        )
        save_btn.pack(side="left", padx=10)

    def add_product_row(self):
        row_frame = ctk.CTkFrame(
            self.products_container,
            fg_color=COLORS["primary_bg"],
            border_width=2,
            border_color=COLORS["secondary_bg"],
            corner_radius=6,
        )
        row_frame.pack(fill="x", pady=5)

        inner_frame = ctk.CTkFrame(row_frame, fg_color=COLORS["primary_bg"])
        inner_frame.pack(fill="x", padx=10, pady=10)

        inner_frame.grid_columnconfigure(0, weight=3)
        inner_frame.grid_columnconfigure(1, weight=1)

        article_label = ctk.CTkLabel(
            inner_frame, text="Артикул товара", font=("Times New Roman", 10, "bold"), text_color=COLORS["text_gray"]
        )
        article_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        article_entry = ctk.CTkEntry(
            inner_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            placeholder_text="Введите артикул",
        )
        article_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        qty_label = ctk.CTkLabel(
            inner_frame, text="Количество", font=("Times New Roman", 10, "bold"), text_color=COLORS["text_gray"]
        )
        qty_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        qty_entry = ctk.CTkEntry(
            inner_frame,
            font=("Times New Roman", 12),
            border_width=2,
            border_color=COLORS["secondary_bg"],
            fg_color=COLORS["primary_bg"],
            placeholder_text="Кол-во",
            width=100,
        )
        qty_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        delete_btn = ctk.CTkButton(
            inner_frame,
            text="🗑️",
            width=40,
            font=("Times New Roman", 16),
            fg_color=COLORS["discount_bg"],
            hover_color="#246B43",
            text_color="#FFFFFF",
            command=lambda: row_frame.destroy(),
        )
        delete_btn.grid(row=1, column=2)

        self.order_products.append((article_entry, qty_entry))

    def save(self):
        try:
            order_date_str = self.order_date_entry.get().strip()
            delivery_date_str = self.delivery_date_entry.get().strip()
            client_name = self.client_entry.get().strip()
            code_str = self.code_entry.get().strip()
            status = self.status_var.get()

            if not all([order_date_str, delivery_date_str, client_name, code_str]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return

            try:
                code = int(code_str)
            except:
                messagebox.showerror("Ошибка", "Неверный формат кода получения")
                return

            pickup_address = self.pickup_var.get()
            pickup_point = next((p for p in self.parent.pickup_points_cache if p["address"] == pickup_address), None)
            if not pickup_point:
                messagebox.showerror("Ошибка", "Выберите пункт выдачи")
                return

            products = []
            for article_entry, qty_entry in self.order_products:
                article = article_entry.get().strip()
                qty_str = qty_entry.get().strip()

                if article and qty_str:
                    try:
                        qty = int(qty_str)
                        products.append({"product_id": article, "quantity": qty})
                    except:
                        messagebox.showerror("Ошибка", f"Неверное количество для товара {article}")
                        return

            if not products:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один товар")
                return

            data = {
                "order_date": order_date_str,
                "delivery_date": delivery_date_str,
                "pickup_point_id": pickup_point["id"],
                "client_full_name": client_name,
                "code": code,
                "status": status,
                "products": products,
            }

            headers = {"Authorization": f"Bearer {self.parent.access_token}", "Content-Type": "application/json"}

            if self.mode == "add":
                response = requests.post(f"{API_BASE_URL}/api/orders", json=data, headers=headers, timeout=5)
            else:
                response = requests.put(
                    f"{API_BASE_URL}/api/orders/{self.order['id']}", json=data, headers=headers, timeout=5
                )

            if response.status_code in [200, 201]:
                messagebox.showinfo("Успех", "Заказ успешно сохранен")
                self.parent.load_orders()
                self.destroy()
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Ошибка валидации")
                messagebox.showerror("Ошибка", error_detail)
            elif response.status_code == 404:
                messagebox.showerror("Ошибка", "Один или несколько товаров не найдены")
            else:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {response.status_code}")

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заказ:\n{str(e)}")


if __name__ == "__main__":
    app = ShoeShopApp()
    app.mainloop()
