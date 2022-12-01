from algosdk.v2client.algod import AlgodClient

class AlgorandBlocks:
    def __init__(self, ac: AlgodClient, current_round=-1):
        self.ac = ac
        self.last_round = 0
        self.current_round = current_round

    def __iter__(self):
        status = self.ac.status()
        self.last_round = status['last-round']

        if self.current_round == -1:
            self.current_round = self.last_round

        return self

    def __next__(self):
        if self.current_round >= self.last_round:
            status = self.ac.status_after_block(self.last_round)
            self.last_round = status['last-round']

        block = self.ac.block_info(self.current_round)
        self.current_round += 1

        return block


class Algorand:
    def __init__(self, ac: AlgodClient = None):
        if ac is None:
            ac = AlgodClient("", "https://mainnet-api.algonode.cloud")

        self.ac = ac

    def blocks(self, start_round: int = -1):
        return AlgorandBlocks(self.ac, start_round)

if __name__ == '__main__':
    a = Algorand()
    blocks = a.blocks()

    for block in blocks:
        for tx in block['block'].get('txns', []):
            print(tx)
