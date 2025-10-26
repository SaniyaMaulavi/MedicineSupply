import streamlit as st
import hashlib
import json
from datetime import datetime

# ---------------- BLOCKCHAIN CLASS ---------------- #
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def add_transaction(self, medicine_name, quantity, from_entity, to_entity):
        transaction = {
            'medicine_name': medicine_name,
            'quantity': quantity,
            'from': from_entity,
            'to': to_entity
        }
        self.current_transactions.append(transaction)
        return self.last_block()['index'] + 1

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


# ---------------- STREAMLIT SETUP ---------------- #
st.set_page_config(page_title="Medicine Supply Blockchain", layout="wide", page_icon="💊")

# ---------------- SESSION SETUP ---------------- #
if "blockchain" not in st.session_state:
    st.session_state.blockchain = Blockchain()
if "users" not in st.session_state:
    st.session_state.users = {}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------------- SIGNUP ONLY ---------------- #
if not st.session_state.logged_in:
    st.markdown('<h1 style="text-align:center; color:#5BC0BE;">💊 Medicine Supply Chain Blockchain</h1>', unsafe_allow_html=True)
    st.write("A secure blockchain-based medicine tracking system.")

    with st.form("signup_form"):
        signup_user_input = st.text_input("Create Username", key="signup_username")
        signup_pw_input = st.text_input("Create Password", type="password", key="signup_password")
        signup_submit = st.form_submit_button("Sign Up")

    if signup_submit:
        u = (signup_user_input or "").strip()
        p = (signup_pw_input or "").strip()
        if not u or not p:
            st.error("Please fill both username and password.")
        elif u in st.session_state.users:
            st.warning("Username already exists! Choose another.")
        else:
            # Save user and auto-login
            st.session_state.users[u] = hashlib.sha256(p.encode()).hexdigest()
            st.session_state.logged_in = True
            st.session_state.current_user = u
            st.success("✅ Signup successful! You are now logged in.")
            st.rerun()  # UPDATED HERE

# ---------------- LOGGED-IN INTERFACE ---------------- #
else:
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("", ["🏠 Home", "📜 View Blockchain", "➕ Add Medicine Record", "🚪 Logout"])
    blockchain = st.session_state.blockchain

    if menu == "🚪 Logout":
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.success("Logged out successfully!")
        st.rerun()  # UPDATED HERE

    elif menu == "🏠 Home":
        st.markdown("<h2>Welcome to Medicine Supply Blockchain</h2>", unsafe_allow_html=True)
        st.write(f"👋 Hello, **{st.session_state.current_user}**! Manage your medicine records securely with blockchain.")
        st.info("Navigate from the sidebar to add or view transactions securely.")

    elif menu == "📜 View Blockchain":
        st.markdown("<h2>📦 Blockchain Ledger</h2>", unsafe_allow_html=True)
        for block in blockchain.chain:
            st.markdown(f"<div style='background-color:#1C2541;padding:10px;margin-bottom:10px;border-radius:10px;border:1px solid #3A506B;'>"
                        f"<b>Block #{block['index']}</b><br>"
                        f"<b>Timestamp:</b> {block['timestamp']}<br>"
                        f"<b>Proof:</b> {block['proof']}<br>"
                        f"<b>Previous Hash:</b> {block['previous_hash']}<br>"
                        f"<b>Transactions:</b><br>",
                        unsafe_allow_html=True)

            if len(block['transactions']) == 0:
                st.markdown("<div style='background-color:#3A506B;padding:5px;border-radius:5px;margin:5px 0;'>No transactions in this block.</div>", unsafe_allow_html=True)
            else:
                for tx in block['transactions']:
                    st.markdown(f"<div style='background-color:#3A506B;padding:5px;border-radius:5px;margin:5px 0;'>💊 {tx['medicine_name']} | Qty: {tx['quantity']} | From: {tx['from']} → To: {tx['to']}</div>",
                                unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "➕ Add Medicine Record":
        st.markdown("<h2>➕ Add New Medicine Transaction</h2>", unsafe_allow_html=True)
        with st.form("add_form", clear_on_submit=True):
            med_name = st.text_input("Medicine Name")
            qty = st.number_input("Quantity", min_value=1, value=1)
            sender = st.text_input("From ")
            receiver = st.text_input("To ")
            submit = st.form_submit_button("Add to Blockchain")

            if submit:
                if med_name and sender and receiver:
                    blockchain.add_transaction(med_name, qty, sender, receiver)
                    last_proof = blockchain.last_block()['proof']
                    proof = blockchain.proof_of_work(last_proof)
                    prev_hash = blockchain.hash(blockchain.last_block())
                    blockchain.create_block(proof, prev_hash)
                    st.success(f"✅ Transaction added! New Block #{len(blockchain.chain)} created.")
                else:
                    st.error("Please fill all fields before adding.")
