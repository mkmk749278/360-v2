"""Server-side execution security primitives.

This package holds the building blocks for Lumin's server-side order
execution custody model (per ``OWNER_BRIEF §3.9`` + ``B18``):

* :mod:`src.security.envelope_crypto` — AES-256-GCM helpers used to
  encrypt per-user Binance API secrets with a per-user data
  encryption key (DEK).  Pure-Python, no GCP dependency.
* :mod:`src.security.kms_client` — Cloud KMS wrapper.  Encrypts /
  decrypts the per-user DEK using a key whose master material
  (KEK) lives inside the GCP HSM and never leaves it.
* :mod:`src.security.firestore_keystore` — per-user encrypted-key
  blob CRUD on top of the Firestore Admin SDK.

The envelope encryption flow these three modules implement:

* **Provision** a new user's key (one-off):
   1. Generate a 32-byte DEK with :func:`envelope_crypto.generate_dek`.
   2. AES-GCM-encrypt the Binance API secret with the DEK
      (:func:`envelope_crypto.encrypt_secret`).
   3. KMS-encrypt the DEK with :meth:`kms_client.KmsClient.encrypt`.
   4. Persist ``{encrypted_secret, encrypted_dek}`` to Firestore.
   5. Wipe the plaintext DEK and plaintext secret from memory.

* **Sign** a request (every order):
   1. Read the user's ``{encrypted_secret, encrypted_dek}`` blob.
   2. KMS-decrypt the DEK (:meth:`kms_client.KmsClient.decrypt`).
   3. AES-GCM-decrypt the secret (:func:`envelope_crypto.decrypt_secret`).
   4. Sign the Binance request body.
   5. Drop references to the plaintext secret.  Never log, never
      return to callers outside the signing service.

A Firestore-only breach yields ciphertext + encrypted DEKs that
cannot be opened without calling KMS — which the breach attacker
cannot do without the signing service's IAM role.  This is the
property ``OWNER_BRIEF B18`` requires.
"""
