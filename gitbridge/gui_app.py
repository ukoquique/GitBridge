#!/usr/bin/env python3
"""
GUI for GitBridge using Tkinter.
Allows users to manage GitHub accounts and repositories through a window interface.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from gitbridge.config_manager import ConfigManager
from gitbridge.github_api import GitHubClient, parse_repository_path
from gitbridge.git_operations import GitRepoSync

class GitBridgeGUI:
    def __init__(self):
        self.config = ConfigManager()
        self.root = tk.Tk()
        self.root.title("GitBridge GUI")
        # Initialize variables for menus
        self.copy_source_var = tk.StringVar()
        self.copy_dest_var = tk.StringVar()
        self.del_account_var = tk.StringVar()
        self.move_dest_var = tk.StringVar()
        self.view_account_var = tk.StringVar()
        self.view_repo_var = tk.StringVar()
        # Create all widgets
        self.create_widgets()
        # Update menus after all widgets are created
        self.update_account_menus()
        self.root.mainloop()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        # Clear list entries until user hits Refresh
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

        # Add Account tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Add Account")
        self.build_add_account(frame)

        # List Repos tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="List Repos")
        self.build_list_repos(frame)

        # Copy Repo tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Copy Repo")
        self.build_copy_repo(frame)

        # Delete Repo tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Delete Repo")
        self.build_delete_repo(frame)

        # Move Repo tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Move Repo")
        self.build_move_repo(frame)

        # View Repo tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="View Repo")
        self.build_view_repo(frame)

    def build_add_account(self, frame):
        ttk.Label(frame, text="Account Name:").grid(row=0, column=0, sticky='w')
        self.add_name = tk.Entry(frame)
        self.add_name.grid(row=0, column=1, sticky='ew')
        ttk.Label(frame, text="Token:").grid(row=1, column=0, sticky='w')
        self.add_token = tk.Entry(frame, show="*")
        self.add_token.grid(row=1, column=1, sticky='ew')
        btn = ttk.Button(frame, text="Add Account", command=self.add_account)
        btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Add a separator
        ttk.Separator(frame, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Add existing accounts display
        ttk.Label(frame, text="Existing Accounts:", font=('TkDefaultFont', 10, 'bold')).grid(row=4, column=0, columnspan=2, sticky='w', pady=(5, 0))
        
        # Create a frame for the accounts list
        accounts_frame = ttk.Frame(frame)
        accounts_frame.grid(row=5, column=0, columnspan=2, sticky='nsew', pady=5)
        
        # Create a scrolled text widget to display accounts
        self.accounts_text = scrolledtext.ScrolledText(accounts_frame, width=40, height=10, wrap=tk.WORD)
        self.accounts_text.pack(fill='both', expand=True)
        self.accounts_text.config(state='disabled')  # Make it read-only
        
        # Refresh button for accounts
        refresh_btn = ttk.Button(frame, text="Refresh Accounts", command=self.refresh_accounts_display)
        refresh_btn.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Configure the frame to expand
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(5, weight=1)  # Make the accounts list expandable
        
        # Initial display of accounts
        self.refresh_accounts_display()

    def build_list_repos(self, frame):
        btn = ttk.Button(frame, text="Refresh", command=self.list_repos)
        btn.pack(anchor='nw', pady=5)
        self.list_text = scrolledtext.ScrolledText(frame, width=80, height=20)
        self.list_text.pack(fill='both', expand=True)

    def build_copy_repo(self, frame):
        labels = ["Repo (owner/name):", "Source:", "Destination:", "Branch:"]
        self.copy_repo_entry = tk.Entry(frame)
        self.copy_branch = tk.Entry(frame)
        self.copy_branch.insert(0, "main")
        self.copy_source_menu = ttk.OptionMenu(frame, self.copy_source_var, '')
        self.copy_dest_menu = ttk.OptionMenu(frame, self.copy_dest_var, '')
        widgets = [self.copy_repo_entry,
                   self.copy_source_menu,
                   self.copy_dest_menu,
                   self.copy_branch]
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky='w', pady=2)
            widgets[i].grid(row=i, column=1, sticky='ew', pady=2)
        btn = ttk.Button(frame, text="Copy Repo", command=self.copy_repo)
        btn.grid(row=len(labels), column=0, columnspan=2, pady=5)
        frame.columnconfigure(1, weight=1)

    def build_delete_repo(self, frame):
        ttk.Label(frame, text="Repo (owner/name):").grid(row=0, column=0, sticky='w', pady=2)
        self.del_repo_entry = tk.Entry(frame)
        self.del_repo_entry.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Label(frame, text="Account:").grid(row=1, column=0, sticky='w', pady=2)
        self.del_account_menu = ttk.OptionMenu(frame, self.del_account_var, '')
        self.del_account_menu.grid(row=1, column=1, sticky='ew', pady=2)
        # Warning before deletion
        ttk.Label(frame, text="Warning: Deleting a repo is irreversible!", foreground="red").grid(row=2, column=0, columnspan=2, pady=2)
        btn = ttk.Button(frame, text="Delete Repo", command=self.delete_repo)
        btn.grid(row=3, column=0, columnspan=2, pady=5)
        frame.columnconfigure(1, weight=1)

    def build_move_repo(self, frame):
        ttk.Label(frame, text="Repo (owner/name):").grid(row=0, column=0, sticky='w', pady=2)
        self.move_repo_entry = tk.Entry(frame)
        self.move_repo_entry.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Label(frame, text="Destination:").grid(row=1, column=0, sticky='w', pady=2)
        self.move_dest_menu = ttk.OptionMenu(frame, self.move_dest_var, '')
        self.move_dest_menu.grid(row=1, column=1, sticky='ew', pady=2)
        btn = ttk.Button(frame, text="Move Repo", command=self.move_repo)
        btn.grid(row=2, column=0, columnspan=2, pady=5)
        frame.columnconfigure(1, weight=1)

    def build_view_repo(self, frame):
        ttk.Label(frame, text="Account:").grid(row=0, column=0, sticky='w', pady=2)
        self.view_account_menu = ttk.OptionMenu(frame, self.view_account_var, '')
        self.view_account_menu.grid(row=0, column=1, sticky='ew', pady=2)
        ttk.Label(frame, text="Repo:").grid(row=1, column=0, sticky='w', pady=2)
        # Editable combobox for repos
        self.view_repo_combo = ttk.Combobox(frame, textvariable=self.view_repo_var, values=[], state='normal')
        self.view_repo_combo.grid(row=1, column=1, sticky='ew', pady=2)
        btn = ttk.Button(frame, text="Refresh", command=self.view_repo)
        btn.grid(row=2, column=0, columnspan=2, pady=5)
        # File listbox to display files and directories
        self.file_listbox = tk.Listbox(frame, height=15)
        self.file_listbox.grid(row=3, column=0, columnspan=2, sticky='nsew')
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=2, sticky='ns')
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        # Text area for file content
        ttk.Label(frame, text="File Content:").grid(row=4, column=0, columnspan=2, sticky='w', pady=(5,0))
        self.file_content_text = scrolledtext.ScrolledText(frame, width=80, height=15)
        self.file_content_text.grid(row=5, column=0, columnspan=3, sticky='nsew')
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)
        frame.rowconfigure(5, weight=2)
        self.view_account_var.trace_add('write', lambda *args: self.update_view_repo_menu())

    def update_account_menus(self):
        accounts = list(self.config.get_accounts().keys())
        var_menu_pairs = [
            (self.copy_source_var, self.copy_source_menu),
            (self.copy_dest_var, self.copy_dest_menu),
            (self.del_account_var, self.del_account_menu),
            (self.move_dest_var, self.move_dest_menu)
        ]
        if hasattr(self, 'view_account_menu'):
            var_menu_pairs.append((self.view_account_var, self.view_account_menu))
        for var, menu in var_menu_pairs:
            menu['menu'].delete(0, 'end')
            for acc in accounts:
                menu['menu'].add_command(
                    label=acc,
                    command=lambda v=var, a=acc: v.set(a)
                )
            var.set(accounts[0] if accounts else '')
        # Refresh view repo options
        if hasattr(self, 'update_view_repo_menu'):
            self.update_view_repo_menu()

    def add_account(self):
        name = self.add_name.get().strip()
        token = self.add_token.get().strip()
        if not name or not token:
            messagebox.showerror("Error", "Name and token required.")
            return
            
        # Check if an account with the same GitHub username already exists
        exists, existing_name = self.config.account_exists_by_username(token)
        if exists:
            messagebox.showerror(
                "Error", 
                f"Cannot add account: A GitHub account with the same username already exists as '{existing_name}'."
            )
            return
            
        success = self.config.add_account(name, token)
        if success:
            messagebox.showinfo("Success", f"Account '{name}' added.")
            # Clear the entry fields
            self.add_name.delete(0, tk.END)
            self.add_token.delete(0, tk.END)
            # Refresh the accounts display
            self.refresh_accounts_display()
            # Update all account menus
            self.update_account_menus()
        else:
            messagebox.showerror("Error", "Failed to add account.")

    def list_repos(self):
        self.list_text.delete('1.0', tk.END)
        for name, token in self.config.get_accounts().items():
            self.list_text.insert(tk.END, f"Account: {name}\n")
            client = GitHubClient(token)
            success, repos = client.list_repositories()
            if success and isinstance(repos, list):
                for repo in repos:
                    self.list_text.insert(tk.END, f"{repo['full_name']}\n")
            else:
                self.list_text.insert(tk.END, f"  Error: {repos}\n")
            self.list_text.insert(tk.END, "\n")

    def copy_repo(self):
        repo_path = self.copy_repo_entry.get().strip()
        src = self.copy_source_var.get().strip()
        dst = self.copy_dest_var.get().strip()
        branch = self.copy_branch.get().strip()
        if not (repo_path and src and dst):
            messagebox.showerror("Error", "Repo, source, and destination required.")
            return
        src_token = self.config.get_accounts().get(src)
        dst_token = self.config.get_accounts().get(dst)
        if not src_token or not dst_token:
            messagebox.showerror("Error", "Invalid source or destination account.")
            return
        src_client = GitHubClient(src_token)
        dst_client = GitHubClient(dst_token)
        success, src_repo = src_client.get_repository(repo_path)
        if not success:
            messagebox.showerror("Error", f"Failed to access source repo: {src_repo}")
            return
        dest_user_ok, dest_user = dst_client.get_user()
        if not dest_user_ok:
            messagebox.showerror("Error", "Failed to access destination account.")
            return
        repo_name = src_repo.get('name')
        dest_full = f"{dest_user['login']}/{repo_name}"
        if not dst_client.repository_exists(dest_full):
            created, result = dst_client.create_repository(
                repo_name,
                private=src_repo.get('private', False),
                description=src_repo.get('description', '')
            )
            if not created:
                messagebox.showerror("Error", f"Failed to create destination repo: {result}")
                return
        source_url = src_repo['clone_url'].replace("https://", f"https://{src_token}@")
        dest_url = f"https://{dst_token}@github.com/{dest_full}.git"
        ok, msg, b = GitRepoSync.copy_repository(source_url, dest_url, branch)
        if ok:
            messagebox.showinfo("Success", f"Copied to {dest_full} on branch {b}")
        else:
            messagebox.showerror("Error", msg)

    def delete_repo(self):
        repo_input = self.del_repo_entry.get().strip()
        if not repo_input:
            messagebox.showerror("Error", "Repo required.")
            return
        # Determine full repo path and client based on input
        if '/' in repo_input:
            try:
                owner, repo_name = parse_repository_path(repo_input)
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            full = repo_input
            # Find matching account token for this owner
            found_token = None
            for label, token in self.config.get_accounts().items():
                ok_u, uname = GitHubClient(token).get_username()
                if ok_u and uname == owner:
                    found_token = token
                    break
            if not found_token:
                messagebox.showerror("Error", f"Account for owner '{owner}' not configured.")
                return
            client = GitHubClient(found_token)
        else:
            repo_name = repo_input
            acc = self.del_account_var.get().strip()
            if not acc:
                messagebox.showerror("Error", "Account required.")
                return
            token = self.config.get_accounts().get(acc)
            if not token:
                messagebox.showerror("Error", f"Account '{acc}' not found.")
                return
            client = GitHubClient(token)
            ok, user = client.get_user()
            if not ok:
                messagebox.showerror("Error", "Failed to get user info.")
                return
            full = f"{user['login']}/{repo_name}"
        if not client.repository_exists(full):
            messagebox.showerror("Error", f"Repository {full} not found.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {full}? This cannot be undone."):
            return
        d_ok, res = client.delete_repository(full)
        if d_ok:
            messagebox.showinfo("Success", f"Deleted {full}")
        else:
            messagebox.showerror("Error", f"Failed to delete: {res}")

    def move_repo(self):
        # Get repo info from move repo tab
        repo_path = self.move_repo_entry.get().strip()
        # Derive source account from repo name
        try:
            owner, _ = parse_repository_path(repo_path)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        src = owner
        dst = self.move_dest_var.get().strip()
        # Validate source account exists
        if src not in self.config.get_accounts():
            messagebox.showerror("Error", f"Source account '{src}' not found.")
            return
        if not (repo_path and src and dst):
            messagebox.showerror("Error", "Repo, source, and destination required.")
            return
        
        # Create a wait indicator
        wait_window = tk.Toplevel(self.root)
        wait_window.title("Processing")
        wait_window.geometry("300x100")
        wait_window.transient(self.root)  # Set to be on top of the main window
        wait_window.grab_set()  # Modal window
        
        # Center the window
        wait_window.update_idletasks()
        width = wait_window.winfo_width()
        height = wait_window.winfo_height()
        x = (wait_window.winfo_screenwidth() // 2) - (width // 2)
        y = (wait_window.winfo_screenheight() // 2) - (height // 2)
        wait_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Add a message and progress indicator
        ttk.Label(wait_window, text=f"Moving repository {repo_path}\nPlease wait...", 
                 justify=tk.CENTER).pack(pady=10)
        progress = ttk.Progressbar(wait_window, mode='indeterminate')
        progress.pack(fill=tk.X, padx=20, pady=10)
        progress.start()
        
        # Schedule the actual operation to allow the wait window to render
        def perform_move():
            try:
                # Set values in copy repo fields
                self.copy_repo_entry.delete(0, tk.END)
                self.copy_repo_entry.insert(0, repo_path)
                self.copy_source_var.set(src)
                self.copy_dest_var.set(dst)
                
                # Set values in delete repo fields
                self.del_repo_entry.delete(0, tk.END)
                self.del_repo_entry.insert(0, repo_path)
                self.del_account_var.set(src)
                
                # Perform the copy operation
                self.copy_repo()
                # Perform the delete operation
                self.delete_repo()
            finally:
                # Close the wait window when done
                wait_window.destroy()
        
        # Schedule the operation to run after a short delay
        self.root.after(100, perform_move)

    def update_view_repo_menu(self):
        acc = self.view_account_var.get()
        token = self.config.get_accounts().get(acc)
        if not token:
            return
        client = GitHubClient(token)
        ok, repos = client.list_repositories()
        if not ok or not isinstance(repos, list):
            return
        names = [r['full_name'] for r in repos]
        # Update combobox values to allow typing or selection
        self.view_repo_combo['values'] = names
        if names:
            self.view_repo_var.set(names[0])

    def view_repo(self):
        self.file_listbox.delete(0, tk.END)
        self.file_content_text.delete('1.0', tk.END)
        repo = self.view_repo_var.get().strip()
        acc = self.view_account_var.get().strip()
        if not (repo and acc):
            messagebox.showerror("Error", "Account and repo required.")
            return
        token = self.config.get_accounts().get(acc)
        client = GitHubClient(token)
        ok, items = client.list_repository_contents(repo)
        if not ok:
            messagebox.showerror("Error", f"Failed to list contents: {items}")
            return
        if isinstance(items, list):
            for it in items:
                self.file_listbox.insert(tk.END, it['name'])
        else:
            messagebox.showerror("Error", f"{items}")

    def on_file_select(self, event):
        sel = event.widget.curselection()
        if not sel:
            return
        name = event.widget.get(sel[0])
        repo = self.view_repo_var.get().strip()
        acc = self.view_account_var.get().strip()
        if not (repo and acc):
            return
        token = self.config.get_accounts().get(acc)
        client = GitHubClient(token)
        ok, data = client.list_repository_contents(repo, name)
        if not ok:
            messagebox.showerror("Error", f"Failed getting contents: {data}")
            return
        self.file_content_text.delete('1.0', tk.END)
        if isinstance(data, list):
            for it in data:
                self.file_content_text.insert(tk.END, f"{it['type']}  {it['name']}\n")
        elif isinstance(data, dict):
            content = data.get('content', '')
            if data.get('encoding') == 'base64':
                import base64
                try:
                    decoded = base64.b64decode(content).decode('utf-8', errors='ignore')
                except Exception:
                    decoded = content
            else:
                decoded = content
            self.file_content_text.insert(tk.END, decoded)
        else:
            self.file_content_text.insert(tk.END, str(data))

    def refresh_accounts_display(self):
        """Refresh the display of existing accounts in the Add Account tab."""
        # Enable editing
        self.accounts_text.config(state='normal')
        # Clear current content
        self.accounts_text.delete('1.0', tk.END)
        
        # Get accounts and display them
        accounts = self.config.get_accounts()
        if accounts:
            for name, token in accounts.items():
                # Show account name and masked token
                masked_token = token[:4] + '...' + token[-4:] if len(token) > 8 else '****'
                self.accounts_text.insert(tk.END, f"Name: {name}\nToken: {masked_token}\n")
                # Add delete button for this account
                delete_btn = ttk.Button(self.accounts_text, text="Delete", 
                                      command=lambda n=name: self.delete_account(n))
                self.accounts_text.window_create(tk.END, window=delete_btn)
                self.accounts_text.insert(tk.END, "\n\n")
        else:
            self.accounts_text.insert(tk.END, "No accounts configured yet.\n")
            
        # Disable editing again
        self.accounts_text.config(state='disabled')
        
    def delete_account(self, name):
        """Delete an account from the configuration."""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete account '{name}'?"):
            if self.config.remove_account(name):
                messagebox.showinfo("Success", f"Account '{name}' deleted.")
                # Refresh the accounts display
                self.refresh_accounts_display()
                # Update all account menus
                self.update_account_menus()
            else:
                messagebox.showerror("Error", f"Failed to delete account '{name}'.")

    def on_tab_changed(self, event):
        # Clear repo list when opening List Repos tab
        try:
            selected = event.widget.tab(event.widget.index('current'))['text']
            if selected == 'List Repos' and hasattr(self, 'list_text'):
                self.list_text.delete('1.0', tk.END)
        except Exception:
            pass

if __name__ == '__main__':
    GitBridgeGUI()
