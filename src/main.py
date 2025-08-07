"""
Main entry point for the Portfolio Tracker application.
Handles authentication and navigation between views.
"""

import flet as ft
from typing import Optional

from src.utils.config import get_config, COLORS
from src.utils.crypto import get_security_manager
from src.core.database import get_db_manager
from src.gui.dashboard import DashboardView


class AuthenticationView:
    """Handles master password authentication."""
    
    def __init__(self, page: ft.Page, on_success_callback):
        self.page = page
        self.security = get_security_manager()
        self.on_success = on_success_callback
        self.password_field = None
        self.confirm_field = None
        self.error_text = None
        
    def build(self) -> ft.View:
        """Build the authentication view."""
        is_first_run = self.security.is_first_run()
        
        # Title
        title = ft.Text(
            "Welcome to Portfolio Tracker Pro" if is_first_run else "Authentication Required",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=COLORS["on_surface"]
        )
        
        subtitle = ft.Text(
            "Set your master password to secure your data" if is_first_run 
            else "Enter your master password to continue",
            size=14,
            color=COLORS["on_surface_variant"]
        )
        
        # Password field
        self.password_field = ft.TextField(
            label="Master Password",
            password=True,
            can_reveal_password=True,
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"],
            selection_color=COLORS["primary"],
            on_submit=lambda _: self.handle_submit() if not is_first_run else None
        )
        
        # Confirm password field (only for first run)
        self.confirm_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            border_color=COLORS["outline"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"],
            selection_color=COLORS["primary"],
            visible=is_first_run,
            on_submit=lambda _: self.handle_submit() if is_first_run else None
        )
        
        # Error text
        self.error_text = ft.Text(
            "",
            size=12,
            color=COLORS["error"],
            visible=False
        )
        
        # Password requirements (first run only)
        requirements_text = ft.Text(
            self.security.get_password_requirements(),
            size=12,
            color=COLORS["on_surface_variant"],
            visible=is_first_run
        )
        
        # Submit button
        submit_btn = ft.ElevatedButton(
            text="Create Master Password" if is_first_run else "Unlock",
            bgcolor=COLORS["primary"],
            color=COLORS["on_primary"],
            on_click=lambda _: self.handle_submit(),
            width=200,
            height=45
        )
        
        # Security notice
        security_notice = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.SECURITY, color=COLORS["primary"], size=20),
                ft.Text(
                    "Your data is encrypted locally. Never share your master password.",
                    size=11,
                    color=COLORS["on_surface_variant"],
                    expand=True
                )
            ]),
            padding=10,
            bgcolor=COLORS["surface_variant"],
            border_radius=8,
            margin=ft.margin.only(top=20)
        )
        
        # Main container
        content = ft.Container(
            content=ft.Column([
                ft.Container(height=50),
                ft.Icon(ft.icons.LOCK_OUTLINE, color=COLORS["primary"], size=64),
                ft.Container(height=20),
                title,
                subtitle,
                ft.Container(height=30),
                self.password_field,
                self.confirm_field,
                requirements_text,
                self.error_text,
                ft.Container(height=20),
                ft.Row([submit_btn], alignment=ft.MainAxisAlignment.CENTER),
                security_notice,
                ft.Container(height=50),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=450,
            padding=30,
            bgcolor=COLORS["surface"],
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLACK26,
            )
        )
        
        return ft.View(
            "/auth",
            [
                ft.Container(
                    content=content,
                    alignment=ft.alignment.center,
                    expand=True,
                    bgcolor=COLORS["background"]
                )
            ],
            bgcolor=COLORS["background"]
        )
    
    def handle_submit(self):
        """Handle password submission."""
        password = self.password_field.value
        
        if not password:
            self.show_error("Please enter a password")
            return
        
        if self.security.is_first_run():
            # First run - create master password
            confirm = self.confirm_field.value
            
            if password != confirm:
                self.show_error("Passwords do not match")
                return
            
            if len(password) < get_config().PASSWORD_MIN_LENGTH:
                self.show_error(f"Password must be at least {get_config().PASSWORD_MIN_LENGTH} characters")
                return
            
            # Initialize master password
            if self.security.initialize_master_password(password):
                # Initialize database
                db = get_db_manager()
                if db.initialize(check_auth=False):
                    self.on_success()
                else:
                    self.show_error("Failed to initialize database")
            else:
                self.show_error("Password does not meet requirements")
        else:
            # Authenticate existing password
            if self.security.authenticate(password):
                # Initialize database
                db = get_db_manager()
                if db.initialize():
                    self.on_success()
                else:
                    self.show_error("Failed to connect to database")
            else:
                self.show_error("Invalid password")
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_text.value = message
        self.error_text.visible = True
        self.page.update()


class PortfolioTrackerApp:
    """Main application controller."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.config = get_config()
        self.security = get_security_manager()
        self.db = get_db_manager()
        
        # Configure page
        self.page.title = self.config.APP_NAME
        self.page.window_width = self.config.WINDOW_WIDTH
        self.page.window_height = self.config.WINDOW_HEIGHT
        self.page.window_resizable = True
        self.page.theme_mode = ft.ThemeMode.DARK if self.config.THEME_MODE == "dark" else ft.ThemeMode.LIGHT
        self.page.bgcolor = COLORS["background"]
        
        # Views
        self.auth_view = None
        self.dashboard_view = None
        self.current_view = None
        
        # Initialize
        self.initialize()
    
    def initialize(self):
        """Initialize the application."""
        # Check authentication status
        if not self.security.is_authenticated():
            self.show_auth_view()
        else:
            # Try to initialize database
            if self.db.initialize():
                self.show_dashboard()
            else:
                self.show_auth_view()
    
    def show_auth_view(self):
        """Show authentication view."""
        self.auth_view = AuthenticationView(
            self.page,
            on_success_callback=self.on_auth_success
        )
        self.page.views.clear()
        self.page.views.append(self.auth_view.build())
        self.page.update()
    
    def on_auth_success(self):
        """Handle successful authentication."""
        self.show_dashboard()
    
    def show_dashboard(self):
        """Show main dashboard."""
        self.dashboard_view = DashboardView(self.page, self)
        self.page.views.clear()
        self.page.views.append(self.dashboard_view.build())
        self.page.update()
    
    def handle_logout(self):
        """Handle user logout."""
        self.security.logout()
        self.show_auth_view()


def main(page: ft.Page):
    """Main entry point for Flet application."""
    app = PortfolioTrackerApp(page)


if __name__ == "__main__":
    ft.app(target=main)