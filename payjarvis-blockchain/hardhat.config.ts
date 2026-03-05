import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";
import "dotenv/config";

const DEPLOYER_PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY || "0x" + "0".repeat(64);
const POLYGON_RPC_URL = process.env.POLYGON_RPC_URL || "https://polygon-rpc.com";
const AMOY_RPC_URL = process.env.AMOY_RPC_URL || "https://rpc-amoy.polygon.technology";
const POLYGONSCAN_API_KEY = process.env.POLYGONSCAN_API_KEY || "";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  networks: {
    hardhat: {},
    amoy: {
      url: AMOY_RPC_URL,
      accounts: [DEPLOYER_PRIVATE_KEY],
      chainId: 80002,
    },
    polygon: {
      url: POLYGON_RPC_URL,
      accounts: [DEPLOYER_PRIVATE_KEY],
      chainId: 137,
    },
  },
  etherscan: {
    apiKey: {
      polygon: POLYGONSCAN_API_KEY,
      polygonAmoy: POLYGONSCAN_API_KEY,
    },
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },
};

export default config;
