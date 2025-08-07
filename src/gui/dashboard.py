"""
Dashboard view for the Portfolio Tracker.
Main interface showing portfolio overview and navigation.
"""

import flet as ft
from datetime import datetime
from typing import Optional, List, Dict

from src.utils.config import get_config, COLORS
from src.core.database import get_db_manager


class CreateAccountDialog:
    """Dialog for creating new accounts/depots."""
    
    def __init__(self, page: ft.Page, on_create_callback):
        self.page = page
        self.on_create = on_create_callback
        self.db = get_db_manager()
        
        # Form fields
        self.name_field = None
        self.type_dropdown = None
        self.broker_field = None
        self.currency_dropdown = None
        self.initial_balance_field = None
        self.dialog = None
    
    def show(self):
        """Show the create account dialog."""
        # Account name field
        self.name_field = ft.TextField(
            label="Account Name",
            hint_text="e.g., Main Portfolio, Crypto Holdings",
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"],
            autofocus=True
        )
        
        # Account type dropdown
        self.type_dropdown = ft.Dropdown(
            label="Account Type",
            options=[
                ft.dropdown.Option(key="stocks", text="Stocks & ETFs"),
                ft.dropdown.Option(key="crypto", text="Cryptocurrency"),
                ft.dropdown.Option(key="mixed", text="Mixed Assets"),
            ],
            value="stocks",
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
        )
        
        # Broker/Exchange field
        self.broker_field = ft.TextField(
            label="Broker/Exchange (Optional)",
            hint_text="e.g., Interactive Brokers, Binance",
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"]
        )
        
        # Currency dropdown
        self.currency_dropdown = ft.Dropdown(
            label="Base Currency",
            options=[
                ft.dropdown.Option(key="EUR", text="EUR (€)"),
                ft.dropdown.Option(key="USD", text="USD ($)"),
            ],
            value="EUR",
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
        )
        
        # Initial balance field
        self.initial_balance_field = ft.TextField(
            label="Initial Balance (Optional)",
            hint_text="0.00",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"],
            value="0"
        )
        
        # Dialog content
        content = ft.Column([
            ft.Text(
                "Create New Account",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=COLORS["on_surface"]
            ),
            ft.Container(height=10),
            self.name_field,
            self.type_dropdown,
            self.broker_field,
            self.currency_dropdown,
            self.initial_balance_field,
        ],
        width=400,
        spacing=15
        )
        
        # Create dialog
        self.dialog = ft.AlertDialog(
            title=ft.Text("New Account Setup"),
            content=content,
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.close_dialog
                ),
                ft.ElevatedButton(
                    "Create Account",
                    bgcolor=COLORS["primary"],
                    color=COLORS["on_primary"],
                    on_click=self.handle_create
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()
    
    def handle_create(self, e):
        """Handle account creation."""
        # Validate inputs
        name = self.name_field.value
        if not name:
            self.show_error("Account name is required")
            return
        
        account_type = self.type_dropdown.value
        broker = self.broker_field.value or None
        currency = self.currency_dropdown.value
        
        try:
            initial_balance = float(self.initial_balance_field.value or 0)
        except ValueError:
            self.show_error("Invalid initial balance")
            return
        
        # Create account in database
        try:
            account_id = self.db.create_account(
                name=name,
                account_type=account_type,
                broker=broker,
                currency=currency,
                initial_balance=initial_balance
            )
            
            # Close dialog and refresh
            self.close_dialog(e)
            self.on_create()
            
            # Show success message
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Account '{name}' created successfully!"),
                bgcolor=COLORS["success"]
            )
            self.page.snack_bar.open = True
            self.page.update()
            
        except Exception as ex:
            self.show_error(f"Failed to create account: {str(ex)}")
    
    def close_dialog(self, e):
        """Close the dialog."""
        self.dialog.open = False
        self.page.update()
    
    def show_error(self, message: str):
        """Show error message."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=COLORS["error"]
        )
        self.page.snack_bar.open = True
        self.page.update()


class DashboardView:
    """Main dashboard view of the application."""
    
    def __init__(self, page: ft.Page, app_controller):
        self.page = page
        self.app = app_controller
        self.db = get_db_manager()
        self.config = get_config()
        
        # UI components
        self.accounts_container = None
        self.portfolio_value_text = None
        self.nav_rail = None
        
    def build(self) -> ft.View:
        """Build the dashboard view."""
        # Create navigation rail
        self.nav_rail = self.create_navigation_rail()
        
        # Create main content
        main_content = self.create_main_content()
        
        # Create app bar
        app_bar = self.create_app_bar()
        
        return ft.View(
            "/dashboard",
            [
                app_bar,
                ft.Row([
                    self.nav_rail,
                    ft.VerticalDivider(width=1, color=COLORS["outline"]),
                    main_content
                ],
                expand=True
                )
            ],
            bgcolor=COLORS["background"]
        )
    
    def create_app_bar(self) -> ft.AppBar:
        """Create the application bar."""
        return ft.AppBar(
            title=ft.Text(
                self.config.APP_NAME,
                color=COLORS["on_surface"]
            ),
            bgcolor=COLORS["surface"],
            actions=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=COLORS["on_surface_variant"],
                    tooltip="Settings",
                    on_click=lambda _: self.show_settings()
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    icon_color=COLORS["on_surface_variant"],
                    tooltip="Logout",
                    on_click=lambda _: self.app.handle_logout()
                ),
            ],
        )
    
    def create_navigation_rail(self) -> ft.NavigationRail:
        """Create the navigation rail."""
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            bgcolor=COLORS["surface"],
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SHOW_CHART_OUTLINED,
                    selected_icon=ft.Icons.SHOW_CHART,
                    label="Stocks & ETFs",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.CURRENCY_BITCOIN,
                    selected_icon=ft.Icons.CURRENCY_BITCOIN,
                    label="Crypto",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                    selected_icon=ft.Icons.RECEIPT_LONG,
                    label="Transactions",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANALYTICS_OUTLINED,
                    selected_icon=ft.Icons.ANALYTICS,
                    label="Analytics",
                ),
            ],
            on_change=self.handle_navigation,
        )
    
    def create_main_content(self) -> ft.Container:
        """Create the main dashboard content."""
        # Portfolio value card
        portfolio_card = self.create_portfolio_card()
        
        # Accounts section
        accounts_section = self.create_accounts_section()
        
        # Quick stats
        stats_row = self.create_stats_row()
        
        content = ft.Column([
            ft.Container(height=20),
            ft.Text(
                "Portfolio Overview",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=COLORS["on_surface"]
            ),
            ft.Container(height=20),
            portfolio_card,
            ft.Container(height=20),
            stats_row,
            ft.Container(height=30),
            accounts_section,
        ],
        scroll=ft.ScrollMode.AUTO
        )
        
        return ft.Container(
            content=content,
            expand=True,
            padding=30,
        )
    
    def create_portfolio_card(self) -> ft.Container:
        """Create the portfolio value card."""
        self.portfolio_value_text = ft.Text(
            "€0.00",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=COLORS["primary"]
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Total Portfolio Value",
                    size=14,
                    color=COLORS["on_surface_variant"]
                ),
                self.portfolio_value_text,
                ft.Row([
                    ft.Text(
                        "No assets yet",
                        size=12,
                        color=COLORS["on_surface_variant"]
                    ),
                ])
            ]),
            padding=20,
            bgcolor=COLORS["surface"],
            border_radius=10,
            width=400,
        )
    
    def create_stats_row(self) -> ft.Row:
        """Create quick statistics row."""
        stats = [
            {"label": "Accounts", "value": "0", "icon": ft.Icons.ACCOUNT_BALANCE},
            {"label": "Assets", "value": "0", "icon": ft.Icons.PIE_CHART},
            {"label": "24h Change", "value": "0.00%", "icon": ft.Icons.TRENDING_UP},
            {"label": "Total P&L", "value": "€0.00", "icon": ft.Icons.ATTACH_MONEY},
        ]
        
        cards = []
        for stat in stats:
            card = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(stat["icon"], color=COLORS["primary"], size=20),
                        ft.Text(stat["label"], size=12, color=COLORS["on_surface_variant"])
                    ]),
                    ft.Text(
                        stat["value"],
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["on_surface"]
                    )
                ]),
                padding=15,
                bgcolor=COLORS["surface"],
                border_radius=8,
                width=200,
            )
            cards.append(card)
        
        return ft.Row(cards, spacing=20)
    
    def create_accounts_section(self) -> ft.Container:
        """Create the accounts section."""
        # Header with create button
        header = ft.Row([
            ft.Text(
                "Accounts & Depots",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=COLORS["on_surface"]
            ),
            ft.Container(expand=True),
            ft.ElevatedButton(
                "Create Account",
                icon=ft.Icons.ADD,
                bgcolor=COLORS["primary"],
                color=COLORS["on_primary"],
                on_click=lambda _: self.show_create_account_dialog()
            )
        ])
        
        # Accounts container
        self.accounts_container = ft.Column(
            spacing=10,
        )
        
        # Load existing accounts
        self.refresh_accounts()
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Container(height=10),
                self.accounts_container
            ]),
            expand=True
        )
    
    def refresh_accounts(self):
        """Refresh the accounts list."""
        self.accounts_container.controls.clear()
        
        # Get accounts from database
        accounts = self.db.get_accounts()
        
        if not accounts:
            # Show empty state
            empty_state = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                        color=COLORS["on_surface_variant"],
                        size=64
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "No accounts yet",
                        size=18,
                        color=COLORS["on_surface_variant"]
                    ),
                    ft.Text(
                        "Create your first account to start tracking your portfolio",
                        size=14,
                        color=COLORS["on_surface_variant"],
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                bgcolor=COLORS["surface"],
                border_radius=10,
                alignment=ft.alignment.center,
            )
            self.accounts_container.controls.append(empty_state)
        else:
            # Show account cards
            for account in accounts:
                card = self.create_account_card(account)
                self.accounts_container.controls.append(card)
        
        # Update stats
        self.update_stats(len(accounts))
        
        if self.page:
            self.page.update()
    
    def create_account_card(self, account: Dict) -> ft.Container:
        """Create an account card."""
        # Determine icon based on account type
        icon = ft.Icons.SHOW_CHART
        if account['type'] == 'crypto':
            icon = ft.Icons.CURRENCY_BITCOIN
        elif account['type'] == 'mixed':
            icon = ft.Icons.ACCOUNT_BALANCE_WALLET
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=COLORS["primary"], size=32),
                ft.Column([
                    ft.Text(
                        account['name'],
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["on_surface"]
                    ),
                    ft.Text(
                        f"{account['type'].title()} • {account['currency']} • Balance: {account['currency']} {account['initial_balance']:.2f}",
                        size=12,
                        color=COLORS["on_surface_variant"]
                    ),
                    ft.Text(
                        f"Broker: {account['broker'] or 'Not specified'}",
                        size=11,
                        color=COLORS["on_surface_variant"]
                    ),
                ],
                expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_color=COLORS["on_surface_variant"],
                    tooltip="Edit Account",
                    on_click=lambda _, acc=account: self.edit_account(acc)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=COLORS["error"],
                    tooltip="Delete Account",
                    on_click=lambda _, acc=account: self.delete_account(acc)
                ),
            ]),
            padding=15,
            bgcolor=COLORS["surface"],
            border_radius=8,
        )
    
    def update_stats(self, account_count: int):
        """Update statistics display."""
        # This would be expanded to update all stats
        pass
    
    def show_create_account_dialog(self):
        """Show the create account dialog."""
        dialog = CreateAccountDialog(self.page, self.refresh_accounts)
        dialog.show()
    
    def edit_account(self, account: Dict):
        """Edit an existing account."""
        # TODO: Implement edit functionality
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Edit functionality coming soon for: {account['name']}"),
            bgcolor=COLORS["warning"]
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def delete_account(self, account: Dict):
        """Delete an account."""
        # TODO: Implement delete with confirmation
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Delete functionality coming soon for: {account['name']}"),
            bgcolor=COLORS["warning"]
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def handle_navigation(self, e):
        """Handle navigation rail selection."""
        index = e.control.selected_index
        views = ["Dashboard", "Stocks & ETFs", "Crypto", "Transactions", "Analytics"]
        
        if index > 0:
            # Show coming soon message for other views
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{views[index]} view coming soon!"),
                bgcolor=COLORS["warning"]
            )
            self.page.snack_bar.open = True
            self.page.update()
            
            # Reset to dashboard
            e.control.selected_index = 0
            self.page.update()
    
    def show_settings(self):
        """Show settings dialog."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Settings coming soon!"),
            bgcolor=COLORS["warning"]
        )
        self.page.snack_bar.open = True
        self.page.update()