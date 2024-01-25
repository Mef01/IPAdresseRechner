def CheckInputIPv4(inputMsg):
    IPv4 = str(input(inputMsg))
    if len(IPv4) > 15: 
        return -1
    IPv4Split = IPv4.split('.')
    for i in range(4):
        if not isinstance(int(IPv4Split[i]), int):
            return -1
        if int(IPv4Split[i]) > 255:
            return -1
    return IPv4
    
def IPv4_to_Binary(IPv4):
    result = ''
    while IPv4 > 0:
        result = str(IPv4 % 2) + result
        IPv4 //= 2
    return result or '0'



while True:
    IPv4Adresse = CheckInputIPv4('Geben sie bitte ihre IPv4 adresse ein: ')
    if not IPv4Adresse == -1:
        break
    print('Falsche Eingabe, bitte erneut versuchen.')
while True:
    Subnetmask = CheckInputIPv4('Geben sie bitte ihre Subnetmask ein: ')  
    if not Subnetmask == -1:
        break
    print('Falsche Eingabe, bitte erneut versuchen.')

IPv4Split = IPv4Adresse.split('.')
for i in range(4):
    binary = IPv4_to_Binary(int(IPv4Split[i]))
    while len(binary) < 8:
        binary = '0' + binary

    print(binary)
    
    



