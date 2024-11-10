#!/bin/python3

import subprocess
import json
import os

def genPrivKey():
    # Generate private key
    private_key = subprocess.run(
        ['wg', 'genkey'], 
        capture_output=True, 
        text=True
    ).stdout.strip()
    return private_key

def genPubKey(private_key):
    # Generate public key using the private key
        public_key = subprocess.run(
        ['wg', 'pubkey'], 
        input=private_key, 
        capture_output=True, 
        text=True
    ).stdout.strip()
        return public_key

def genKey():
    private_key = genPrivKey()
    public_key = genPubKey(private_key)
    return private_key, public_key


def buildJson(jsonFileName:str):
    d:dict

    with open(jsonFileName, "r") as f:
        d = json.loads(f.read())

    for name, data in d["Networks"].items():
        
        if not "ip" in d["Server"].keys():
            d["Server"]["ip"] = data["serverIp"]
        if not data["serverIp"] in d["Server"]["ip"]:
            d["Server"]["ip"] += ", " + data["serverIp"]

        if not "privateKey" in d["Server"].keys():
            priv_key, pub_key = genKey()
            d["Server"]["privateKey"] = priv_key
            d["Server"]["publicKey"] = pub_key

        if not "publicKey" in d["Server"].keys():
            pub_key = genPubKey()
            d["Server"]["publicKey"] = pub_key

        for i, peer in enumerate(data["peers"]):
            peer:dict
            if not "privateKey" in peer.keys():
                priv_key, pub_key = genKey()
                peer["privateKey"] = priv_key
                peer["publicKey"] = pub_key

            if not "publicKey" in peer.keys():
                peer["publicKey"] = genPubKey(peer["privateKey"])

    with open(jsonFileName, "w") as f:
        f.write(json.dumps(d, indent=4, separators=(", ", " : ")))

def makeFiles(jsonFileName):
    d:dict

    with open(jsonFileName, "r") as f:
        d = json.loads(f.read())
    
    for name, data in d["Networks"].items():
        if not name in os.listdir("."):
            os.mkdir(name)
        
        for i, peer in enumerate(data["peers"]):
            lines = []
            lines.append("[Interface]")
            lines.append("PrivateKey = " + peer["privateKey"])
            lines.append("Adress = " + peer["ip"])
            # lines.append("DNS = 8.8.8.8") # ?
            lines.append("")
            lines.append("[Peer]")
            lines.append("PublicKey = " + d["Server"]["publicKey"])
            lines.append("Endpoint = " + f"{d['Server']["publicIp"]}:{d['Server']["port"]}")
            lines.append("AllowedIPs = " + data["allowedIps"])
            
            with open(f"{name}/{peer['name']}.conf", "w") as f:
                f.write("\n".join(lines))
  
    
    lines = []
    lines.append("[Interface]")
    lines.append("PrivateKey = " + d["Server"]["privateKey"])
    lines.append("Adress = " + d["Server"]["ip"])
    lines.append("ListenPort = " + str(d["Server"]["port"]))
    
    for name, data in d["Networks"].items():
        lines.append("")
        lines.append("# " + name)
        for peer in data["peers"]:
            lines.append("")
            lines.append("[Peer]" + " # " + peer["name"])
            lines.append("PublicKey = " + peer["publicKey"])
            lines.append("AllowedIPs = " + peer["ip"])
            
    
    with open(f"wg0.conf", "w") as f:
                f.write("\n".join(lines))
    
buildJson("data.json")    
makeFiles("data.json")