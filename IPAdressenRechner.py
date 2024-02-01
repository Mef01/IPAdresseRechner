class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def Input_Loop(Amsg: str, Ais_subnet: bool):

    def Wrong_Input():
        #Input Fehler funktion, damit man nicht immer neu schreiben muss.
        print('Falsche Eingabe, bitte erneut versuchen.')

    def Check_IPv4(AIPv4: str):
        #Überprüft die IPv4 Addresse (egal ob Subnet oder IP) auf Komplett-Länge, Integer, Section-Länge, Section-Count und Section-Größe.
        #Bei einem Fehler wird einfach -1 zurückgegeben, sonst die IPv4.
        if len(AIPv4) > 15: 
            return -1
        IPv4_split = AIPv4.split('.')
        for i in range(4):
            if (not isinstance(int(IPv4_split[i]), int) or 
                    len(IPv4_split[i]) > 3 or 
                    not len(IPv4_split) == 4 or 
                    int(IPv4_split[i]) > 255):
                return -1
        return AIPv4
    
    def Check_Subnet_Mask(Asubnet_mask_IPv4: str):
        #Überprüft spezifisch die Subnetmaske darauf, ob es sich um eine Folge von Nullen auf Einsen handelt.
        #Bei einem Fehler wird einfach -1 zurückgegeben, sonst die IPv4.
        subnet_mask_binary = IPv4_to_Binary(Asubnet_mask_IPv4)
        host_bits = Extract_Subnet_Bits(subnet_mask_binary, 'host')
        network_bits = Extract_Subnet_Bits(subnet_mask_binary, 'network')
        if '0' in network_bits or '1' in host_bits:
            return -1
        return subnet_mask_binary
    
    #Lässt den User so lange neue IPv4 Addressen eintippen, bis beide gültig sind.
    while True:
        IPv4 = input(Amsg)
        if Check_IPv4(IPv4) == IPv4:
            if Ais_subnet:
                if Check_Subnet_Mask(IPv4) == -1:
                    Wrong_Input()
                    continue
            return IPv4
        Wrong_Input()

def IPv4_to_Binary(AIPv4: str):

    def Calc_Binary(Asection: int):
        #Rechnet eine Dezimal Zahl in eine Binäre um.
        #Hier ist davon auszugehen, dass die dezimal Zahl nicht mehr als 3 Stellen hat und das Ergebnis immer ein Oktett ist. 
        #Falls es ich am Ende nicht um ein Oktett handelt, werden solange Nullen vorne angehangen bis es 8 Stellen sind.
        result = ''
        while Asection > 0:
            result = str(Asection % 2) + result
            Asection //= 2
        while len(result) < 8:
            result = '0' + result
        return result or '0'
    
    #Splittet die IPv4 in Sections, wandelt diese in binär um und fügt sie dann zusammen.
    IPv4_split = AIPv4.split('.')
    result = ''
    for i in range(4):
        result = result + Calc_Binary(int(IPv4_split[i])) + '.'
    return result[:-1]

def Binary_to_IPv4(Abinary: str):
    
    def Calc_Decimal(Asection: str):
        #Rechnet eine Binäre Zahl in eine Dezimal um.
        #Hier ist davon auszugehen, dass die binäre Zahl ein Oktett ist. 
        result = 0
        j = 0
        for i in range(7, -1, -1):
            result = result + int(Asection[i]) * pow(2, j)
            j = j + 1
        return result
    
    #Splittet die binär in Sections, wandelt diese in dezimal um und fügt sie dann zusammen.
    binary_split = Abinary.split('.')
    result = ''
    for i in range(4):
        result = result + str(Calc_Decimal(binary_split[i])) + '.'
    return result[:-1]

def Extract_Subnet_Bits(Asubnet_mask_binary: str, Ahost_or_network: str):
    #Extrahiert entweder die Host- oder Netzwerk-Bits aus einer Subnet Maske
    pos_zero = Asubnet_mask_binary.find('0')
    if Ahost_or_network == 'host':
        return Asubnet_mask_binary[pos_zero:]
    return Asubnet_mask_binary[:pos_zero]

def Get_Bit_Count(ABits: str):
    #streicht die Punkte und zählt dann die länge
    bits = ABits.replace('.', '')
    return len(bits)

def Get_IP_Count(Asubnet_mask_binary: str):
    #Zählt die Host-bits und nutzt sie als Potenz für die Zahl 2. Am Ende werden 2 für die Broadcast- und Network address abgezogen.
    host_bits = Extract_Subnet_Bits(Asubnet_mask_binary, 'host')
    host_bits = Get_Bit_Count(host_bits)
    return pow(2, host_bits) - 2

def Invert_Subnet_Mask(Asubnet_mask_binary: str):
    #Invertiert die Subnetz Maske
    network_section_new = Extract_Subnet_Bits(Asubnet_mask_binary, 'host').replace('0', '1')
    host_section_new = Extract_Subnet_Bits(Asubnet_mask_binary, 'network').replace('1', '0')
    return host_section_new + network_section_new

def Get_Colored_Subnet(Asubnet_mask_binary: str):
    network_section = '\033[0;37;45m' + Extract_Subnet_Bits(Asubnet_mask_binary, 'network')
    host_section = '\033[0;37;41m' + Extract_Subnet_Bits(Asubnet_mask_binary, 'host')
    return host_section + network_section

def Build_Broadcast_Address(AIP_address_binary: str, Asubnet_mask_binary_inverted: str):
    #Wendet das OR Verfahren auf die IP und Subnet Addresse (invertiert) an um die Broadcast Addresse zu ermitteln.
    #Falls eine oder beide Ziffern auf einer Stelle eine 1 sind, wird auch eine 1 bei der Broadcast address hinzugefügt. Sonst eine 0.
    result = ''
    for i in range(len(AIP_address_binary)):
        if AIP_address_binary[i] == '1' or Asubnet_mask_binary_inverted[i] == '1':
            result = result + '1'
        elif AIP_address_binary[i] == '.':
            result = result + '.'
        else:
            result = result + '0'
    return result

def Build_Network_Address(AIP_address_binary: str, Asubnet_mask_binary: str):
    #Wendet das AND Verfahren auf die IP und Subnet Addresse an um die Network Addresse zu ermitteln.
    #Falls beide Ziffern auf einer Stelle eine 1 sind, wird auch eine 1 bei der Network address hinzugefügt. Sonst eine 0.
    result = ''
    for i in range(len(AIP_address_binary)):
        if AIP_address_binary[i] == '1' and Asubnet_mask_binary[i] == '1':
            result = result + '1'
        elif AIP_address_binary[i] == '.':
            result = result + '.'
        else:
            result = result + '0'
    return result

IP_address_IPv4 = Input_Loop('Geben sie eine IP Addresse ein: ', False)
subnet_mask_IPv4 = Input_Loop('Geben sie bitte eine Subnetz Maske ein: ', True)

IP_address_binary = IPv4_to_Binary(IP_address_IPv4)
print('\nIP Addresse binär: ' + IP_address_binary)
subnet_mask_binary = IPv4_to_Binary(subnet_mask_IPv4) #asdwasd
print('Subnetz Maske binär: ' + f"{bcolors.OKBLUE}" + Extract_Subnet_Bits(subnet_mask_binary, 'network') + f'{bcolors.ENDC}' + Extract_Subnet_Bits(subnet_mask_binary, 'host'))

print('\nHost Bits extrahieren...\n2 mit Anzahl der Host Bits potenzieren...\nBroad- und Netz-Addresse abziehen...')
IP_count = Get_IP_Count(subnet_mask_binary)
print('Anzahl verfügbarer IP Adressen: ' + str(IP_count))

print('\nSubnetz Maske invertieren...')
subnet_mask_binary_inverted = Invert_Subnet_Mask(subnet_mask_binary) #asdwas
print('Subnetz Maske invertiert: ' + subnet_mask_binary_inverted)

print('\nInvertierte Subnetz Maske und IP Addresse mit logischem OR verknüpfen...')
broadcast_address_binary = Build_Broadcast_Address(IP_address_binary, subnet_mask_binary_inverted)
print('Broadcast Addresse binär: ' + broadcast_address_binary)
print('Binäre Broadcast Addresse in IPv4 umwandeln...')
broadcast_address_IPv4 = Binary_to_IPv4(broadcast_address_binary)
print('Broadcast Addresse IPv4: ' + broadcast_address_IPv4)

print('\nSubnetz Maske und IP Addresse mit logischem AND verknüpfen...')
network_address_binary = Build_Network_Address(IP_address_binary, subnet_mask_binary)
print('Netzwerk Addresse binär: ' + network_address_binary)
print('Binäre Netzwerk Addresse in IPv4 umwandeln...')
network_address_IPv4 = Binary_to_IPv4(network_address_binary) 
print('Netzwerk Addresse IPv4: ' + network_address_IPv4)

print('\nEinsen an Subnetz Maske ablesen --> Netzwerkbits...')
network_mask_CIDR = '/' + str(Get_Bit_Count(Extract_Subnet_Bits(subnet_mask_binary, 'network')))
print('Netzmaske in CIDR Notation: ' + network_mask_CIDR)

print('\nEinsen an Subnetz Maske ablesen...')
network_bits_count = str(Get_Bit_Count(Extract_Subnet_Bits(subnet_mask_binary, 'network')))
print('Anzahl der Netzwerk Bits: ' + network_bits_count)

print('\nNullen an Subnetz Maske ablesen...')
host_bits_count = str(Get_Bit_Count(Extract_Subnet_Bits(subnet_mask_binary, 'host')))
print('Anzahl der Host Bits: ' + host_bits_count)





   
    



