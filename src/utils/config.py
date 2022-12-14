METAMASK_PASSWORD = "twentypound"
NON_REINFORCED_GAME_LIMIT = 1

PRIVATE_KEYS = { #address : private key
    "0x82A323000D50CABaEd045A71FDE88e01a8b082d8":"58995c0f29e038d54d94868b8592edc1cbe88f076e24aa91b1a54b5d463317df",
    "0x4043D2508C591f57C1C0d36CF227be5a3ace83d4":"686e075ee398432d1ea14f9acabd93e695f77404bc51d800dab3c0c1aa02fe14",
}

ADDRESSES = { # order of addresses on Metamask extension. The order MUST be the same with order in Metamask.
    "0x82A323000D50CABaEd045A71FDE88e01a8b082d8":"1",
    "0x4043D2508C591f57C1C0d36CF227be5a3ace83d4":"2",
}

GAS_PRICE_LIMIT = 20000 * pow(10,9)
GAS_LIMIT = 300000
MAX_PRIORITY_FEE_PER_GAS = 0

RPC_URL = "https://subnets.avax.network/swimmer/mainnet/rpc" #swimmer network
CHAIN_ID = 73772 #swimmer network
CONTRACT_ADDRESS = "0x9ab9e81Be39b73de3CCd9408862b1Fc6D2144d2B" #crabada_game_contract
