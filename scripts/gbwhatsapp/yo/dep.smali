.class public Lcom/gbwhatsapp/yo/dep;
.super Ljava/lang/Object;


# direct methods
.method static constructor <clinit>()V
    .locals 0

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static md()[B
    .locals 2

    invoke-static {}, Lcom/cow/s/t/Utils;->getBaseMd5()Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    invoke-static {v0, v1}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v0

    return-object v0
.end method

.method public static getYoSig()[Landroid/content/pm/Signature;
    .locals 6

    const/4 v0, 0x1

    new-array v0, v0, [Landroid/content/pm/Signature;

    new-instance v1, Landroid/content/pm/Signature;

    const-string v2, "$&&D$jCCAvCgAw&BAg&ETCU2pDALBgcqhkjOOAQDBQAwfDEL$AkGA1UEBh$CVV$xEzARBgNVBAgTCkNhbGlmb3JuaWExFDASBgNVBAcTC1NhbnRh&ENsYXJh$RYwFAYDVQQKEw1XaGF0c0FwcCBJbm$u$RQwEgYDVQQLEwtFbmdpbmVlcmluZzEU$B&GA1UEAx$LQnJpYW4gQWN0b24wHhcN$TAwNj&1$j$wNzE2WhcNNDQw$jE1$j$wNzE2WjB8$QswCQYDVQQGEwJVUzET$BEGA1UECB$KQ2FsaWZvcm5pYTEU$B&GA1UEBx$LU2FudGEgQ2xhcmExFjAUBgNVBAoTDVdoYXRzQXBw&EluYy4xFDASBgNVBAsTC0VuZ2luZWVyaW5n$RQwEgYDVQQDEwtCcmlhbiBBY3RvbjCCAbgwggEsBgcqhkjOOAQB$&&BHwKBgQD9f1OBHXUSKVLfSpwu7OTn9hG3UjzvRADDHj+AtlEmaUVdQCJR+1k9jVj6v8X1ujD2y5tVbNeBO4AdNG/yZmC3a5lQpaSfn+gEexAiwk+7qdf+t8Yb+DtX58aophUPBPuD9tPFHs$CNVQTWhaR$vZ1864rYdcq7/&iAxmd0UgBxw&VAJdgU&8V&wv$spK5gqLrhAvwWBz1AoGBAPfho&XWmz3ey7yrXDa4V7l5lK+7+jrqgvlXTAs9B4JnUVlXjrrUWU/mcQcQgYC0SRZx&+h$KBYTt88J$oz&puE8FnqLVHyNKOCjrh4rs6Z1kW6jfwv6&TVi8ftiegEkO8yk8b6oUZCJq&Pf4VrlnwaSi2ZegHtVJWQBTDv+z0kqA4GFAAKBgQDRGYtLgWh7zyRtQainJfCpiaUbzjJuh$go4fVWZ&vXHaSHBU1t5w//S0lDK2hiqkj8Kp$WGywVov9eZxZy37V26dEqr/c2m5qZ0E+ynSu7sqUD7kGx/ze&cGT0H+KAVgkGNQCo5Uc0koLRWYHNtYo&vt5R3X6YZylbPftF/8ayWTALBgcqhkjOOAQDBQADLwAwLA&UAKYCp0d6z4QQdyN74JDfQ2WCyi8CFDU$4CaNB+ceVXdKtOrNTQcc0e+t"

    const-string v4, "$"

    const-string v5, "M"

    invoke-virtual {v2, v4, v5}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v2

    const-string v4, "&"

    const-string v5, "I"

    invoke-virtual {v2, v4, v5}, Ljava/lang/String;->replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;

    move-result-object v2

    const/4 v3, 0x0

    invoke-static {v2, v3}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B

    move-result-object v2

    invoke-direct {v1, v2}, Landroid/content/pm/Signature;-><init>([B)V

    aput-object v1, v0, v3

    return-object v0
.end method

.method public static sec()Ljavax/crypto/SecretKey;
    .locals 1

    new-instance v0, Lcom/gbwhatsapp/yo/dep$1;

    invoke-direct {v0}, Lcom/gbwhatsapp/yo/dep$1;-><init>()V

    return-object v0
.end method