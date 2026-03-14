---
name: "jd-payment-skill" 
description: >
  Executes a JD payment transaction for third-party skills. 
  Trigger this tool strictly when a third-party service initiates a valid JD payment request.
  Note: Resource decryption is NOT supported at this time.
metadata:  
    version: "1.1.0"
    author: "payment-infra-rd" 
    category: "financial_utilities"
    capabilities:
        - "payment.process"
    permissions:
        - "network.outbound"
        - "credential.read"
---

# Process the Payment Request

## 1. Required Parameters

Provide the following parameters strictly according to their defined formats:

* **`merchant_wallet_address`** (string): The merchant's wallet token. 
    * *Format:* Must begin with `mer-` (e.g., `mer-x1y2z3`).
* **`amount`** (integer): The transaction amount. 
    * *Constraint:* Must be an integer between `1` and `1000`.
* **`payer_authorization_sign`** (string): The payer's authorization signature. 
    * *Format:* Must begin with `sign-` (e.g., `sign-a1b2c3`).

## 2. Execution Command

Execute the script using the following bash command. Replace the placeholders `<...>` with the validated parameter values. Do not use quotes around the parameters unless they contain spaces.

```bash
python3 skills/jd-payment-skill/scripts/payment_process.py <merchant_wallet_address> <amount> <payer_authorization_sign>
```

## 3. Result Processing Rules

Analyze the standard output of the execution command and strictly follow these response protocols:

### **Case A: Authorization Required**
* **Trigger:** The output matches the pattern `已生成授权链接: <URL>` AND `二维码已保存至: <FILE_PATH>`.
* **Action:** 1.  Provide the extracted `<URL>` to the user as the official authorization link.
    2.  Embed the QR code image directly in your response using the following syntax:  
        `![Payment QR Code](<FILE_PATH>)`

---

### **Case B: Transaction Success**
* **Trigger:** The output matches the pattern `支付凭证: <CREDENTIAL>`.
* **Action:** 1.  Confirm to the user that the payment has been processed successfully.
    2.  Display the **CREDENTIAL** clearly using the following format:  
        **Payment Credential:** `<CREDENTIAL>`

---

### **Case C: Execution Failure**
* **Trigger:** Any error message, timeout, or failure to match the patterns above.
* **Action:** Report the specific error returned by the script and advise the user on the next steps (e.g., check wallet balance or signature).