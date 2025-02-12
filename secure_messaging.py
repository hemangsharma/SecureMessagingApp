import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import os

class EncryptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Messaging Service")
        self.root.geometry("500x500")

        self.private_key = None
        self.public_key = None
        self.private_key_path = None
        self.public_key_path = None

        # UI Layout
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI layout."""
        # --------- Key Management Section ---------
        key_frame = tk.LabelFrame(self.root, text="🔑 Key Management", padx=10, pady=10)
        key_frame.pack(fill="both", expand="yes", padx=10, pady=5)

        self.generate_keys_button = tk.Button(key_frame, text="Generate New Keys", command=self.generate_keys)
        self.generate_keys_button.pack(pady=5)

        self.upload_private_key_button = tk.Button(key_frame, text="Upload Private Key", command=self.upload_private_key)
        self.upload_private_key_button.pack(pady=5)

        self.upload_public_key_button = tk.Button(key_frame, text="Upload Public Key", command=self.upload_public_key)
        self.upload_public_key_button.pack(pady=5)

        # --------- Encryption Section ---------
        encrypt_frame = tk.LabelFrame(self.root, text="🔒 Encryption", padx=10, pady=10)
        encrypt_frame.pack(fill="both", expand="yes", padx=10, pady=5)

        self.message_label = tk.Label(encrypt_frame, text="Enter your message:")
        self.message_label.pack(pady=5)
        
        self.message_text = tk.Text(encrypt_frame, height=5, width=50)
        self.message_text.pack(pady=5)

        self.encrypt_button = tk.Button(encrypt_frame, text="Encrypt & Save", command=self.encrypt_message)
        self.encrypt_button.pack(pady=5)

        # --------- Decryption Section ---------
        decrypt_frame = tk.LabelFrame(self.root, text="🔓 Decryption", padx=10, pady=10)
        decrypt_frame.pack(fill="both", expand="yes", padx=10, pady=5)

        self.upload_encrypted_file_button = tk.Button(decrypt_frame, text="Upload Encrypted File", command=self.upload_encrypted_file)
        self.upload_encrypted_file_button.pack(pady=5)

        self.decrypt_button = tk.Button(decrypt_frame, text="Decrypt", command=self.decrypt_message)
        self.decrypt_button.pack(pady=5)

    # --------- Key Management Methods ---------
    def generate_keys(self):
        """Generates RSA private and public keys and saves them to files."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Save Private Key
        self.private_key_path = "private_key.pem"
        with open(self.private_key_path, "wb") as priv_file:
            priv_file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save Public Key
        self.public_key_path = "public_key.pem"
        with open(self.public_key_path, "wb") as pub_file:
            pub_file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

        self.private_key = private_key
        self.public_key = public_key

        messagebox.showinfo("Key Generation", "Keys generated and saved as 'private_key.pem' and 'public_key.pem'.")

    def upload_private_key(self):
        """Allows the user to upload an existing private key."""
        file_path = filedialog.askopenfilename(title="Select Private Key", filetypes=[("PEM files", "*.pem")])
        if file_path:
            self.private_key_path = file_path
            with open(file_path, "rb") as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            messagebox.showinfo("Success", "Private key uploaded successfully!")

    def upload_public_key(self):
        """Allows the user to upload an existing public key."""
        file_path = filedialog.askopenfilename(title="Select Public Key", filetypes=[("PEM files", "*.pem")])
        if file_path:
            self.public_key_path = file_path
            with open(file_path, "rb") as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            messagebox.showinfo("Success", "Public key uploaded successfully!")

    # --------- Encryption ---------
    def encrypt_message(self):
        """Encrypts the message using RSA public key and saves it as a file."""
        if not self.public_key:
            messagebox.showerror("Error", "No public key selected. Upload or generate a key first.")
            return

        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Message is empty!")
            return

        try:
            encrypted_message = self.public_key.encrypt(
                message.encode(),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            file_name = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Binary files", "*.bin")])
            if file_name:
                with open(file_name, "wb") as file:
                    file.write(encrypted_message)
                messagebox.showinfo("Success", f"Message encrypted and saved to {file_name}")

        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed: {str(e)}")

    # --------- Decryption ---------
    def upload_encrypted_file(self):
        """Allows the user to upload an encrypted file."""
        file_path = filedialog.askopenfilename(title="Select Encrypted File", filetypes=[("Binary files", "*.bin")])
        if file_path:
            self.encrypted_file_path = file_path
            messagebox.showinfo("Success", "Encrypted file selected!")

    def decrypt_message(self):
        """Decrypts an encrypted file using the selected private key."""
        if not self.private_key:
            messagebox.showerror("Error", "No private key selected. Upload or generate a key first.")
            return
        if not hasattr(self, 'encrypted_file_path'):
            messagebox.showerror("Error", "No encrypted file selected!")
            return

        try:
            with open(self.encrypted_file_path, "rb") as file:
                encrypted_message = file.read()

            decrypted_message = self.private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            messagebox.showinfo("Decrypted Message", decrypted_message.decode())

        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {str(e)}")

# Run Application
if __name__ == "__main__":
    root = tk.Tk()
    app = EncryptionApp(root)
    root.mainloop()