# zero-trust

#### By aplet123
#### Score: 488

Solution script: [solve.py](solve.py)
> If you have any questions, I'll be glad to answer them. You can do so by opening an issue.

## Description

I was researching zero trust proofs in cryptography and now I have zero trust in JWT libraries so I rolled my own! That's what zero trust means, right?

[zero-trust.lac.tf](https://zero-trust.lac.tf)

Note: the flag is in `/flag.txt`

### Downloads: 
[index.js](index.js)

## Write UP

In this challenge, we are presented with a pastebin website. We can input text and save it.

But how does the server keep track of who we are? Apparently there's an `auth` cookie, which contains data that's being used to identify us and keep track of each user's paste.

### How Does the Authentication Work?

Let's look at the code which creates the `auth` cookie:

```javascript
function makeAuth(req, res, next) {
    const iv = crypto.randomBytes(16);
    const tmpfile = "/tmp/pastestore/" + crypto.randomBytes(16).toString("hex");
    fs.writeFileSync(tmpfile, "there's no paste data yet!", "utf8");
    const user = { tmpfile };
    const data = JSON.stringify(user);
    const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
    const ct = Buffer.concat([cipher.update(data), cipher.final()]);
    const authTag = cipher.getAuthTag();
    res.cookie("auth", [iv, authTag, ct].map((x) => x.toString("base64")).join("."));
    res.locals.user = user;
    next();
}
```

So it seems every cookie contains a ciphertext encrypted using `aes-256-gcm`. More specifically, it's made from an `iv`, `authTag` and `ct`, the ciphertext, base64-ed and joined with a dot.

The ciphertext itself contains a javascript object with a path to a temp file, which contains each user's note. An example object would look like this:

```json
{"tmpfile":"/tmp/pastestore/1234567890abcdef"}
```

When we make a `GET` request to `/`, the following code is being run:
```javascript
const [iv, authTag, ct] = auth.split(".").map((x) => Buffer.from(x, "base64"));
const cipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
cipher.setAuthTag(authTag);
res.locals.user = JSON.parse(cipher.update(ct).toString("utf8"));
...
res.type("text/html").send(template.replace("$CONTENT", () => fs.readFileSync(res.locals.user.tmpfile, "utf8")));
```

So if we could somehow change the path of the `tmpfile` to point to `/flag.txt`, when we make a `GET` request to `/` it should contain the flag.

### Modifying the Cookie

We are faced with our first problem: The ciphertext we are trying to modify is being encrypted with a random key we don't know the value of. To understand how we can do that, we first need to understand how AES GCM works.

[AES GCM](https://en.wikipedia.org/wiki/Galois/Counter_Mode) is a symmetric encryption algorithm, which uses counter mode to encrypt data. Counter mode basically works like a [stream cipher](https://en.wikipedia.org/wiki/Stream_cipher): AES GCM receives a key and an IV, and uses it to generate a seemingly random stream of bytes called the encryption stream, which is then being XORed with the plaintext to produce the ciphertext.

So for a given key and IV, you'd always get the same encryption stream.

### Calculating the Encryption Stream

The formula given to calculate a ciphertext at position `i` given an encryption stream `E` is:

![cipher=plaintext_xor_E](https://latex.codecogs.com/svg.latex?cipher_{i}=%20plaintext_{i}%20\oplus%20E_{i})

Because the inverse of the XOR operation is the XOR operation itself, it's possible to rearrange the formula to look like this:

![E=plaintext_xor_cipher](https://latex.codecogs.com/svg.latex?E_{i}=%20plaintext_{i}%20\oplus%20cipher_{i})

So given both the plaintext and the ciphertext, it's possible to calculate the encryption stream.

### Did We Just Break AES?

If you think this was way too easy, you are correct. The `authTag` in AES GCM acts as an anti-tampering mechanism - Each key, IV and ciphertext tuple produce a different `authTag` which can be validated and calculated, but ONLY if you have the key.

Luckily, it was implemented poorly here. Let's look again at the code that deciphers the cookie:
```javascript
const cipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
cipher.setAuthTag(authTag);
res.locals.user = JSON.parse(cipher.update(ct).toString("utf8"));
```

And from the [nodejs documentation](https://nodejs.org/api/crypto.html#deciphersetauthtagbuffer-encoding):

> if the cipher text has been tampered with, `decipher.final()` will throw, indicating that the cipher text should be discarded due to failed authentication

But nowhere in the decryption process is `decipher.final()` being called, so the `authTag` is never validated!

### Implementation

In our scenario, we have all of the ciphertext and a really good estimate of what the plaintext is going to look like. The only part we aren't sure about is the last part of the tmpfile path:

```json
{"tmpfile":"/tmp/pastestore/RANDOMRANDOMRAND"}
```

So let's try to avoid making changes to this part, and stick to the parts of the plaintext we do know. But remember! We need to generate a valid JSON string, or else it won't pass `JSON.parse()`. A possible solution is to generate an evil plaintext which looks like that:

```json
{"tmpfile":"/flag.txt","a":"RANDOMRANDOMRAND"}
```

This will create a valid JSON object with the `tmpfile` pointing to `/flag.txt`!

### The Solution

So the plan is:
1. Fetch a valid `auth` cookie from the server.
2. Calculate the first part of the encryption stream with the known part of the plaintext.
3. Calculate an evil cipher by XORing the first part of the encryption stream with the evil plaintext
4. Concatenate the rest of the original cipher, the part with the random plaintext.
5. Construct an evil cookie from the new values and make a request to the server.

The flag should now appear as your paste!

Solution script: [solve.py](solve.py)
