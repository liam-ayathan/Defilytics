// We require the Hardhat Runtime Environment explicitly here. This is optional
// but useful for running the script in a standalone fashion through `node <script>`.
//
// You can also run a script with `npx hardhat run <script>`. If you do that, Hardhat
// will compile your contracts, add the Hardhat Runtime Environment's members to the
// global scope, and execute the script.

const hre = require("hardhat");
async function main() {
  /*
  DeployContract in ethers.js is an abstraction used to deploy new smart contracts,
  so PriceFeeds here is a factory for instances of our PriceFeeds contract.
  */

  // here we deploy the contract
  const PriceFeeds = await hre.ethers.deployContract("TokenPriceFeeds");
  // wait for the contract to deploy
  await PriceFeeds.waitForDeployment();
  console.log(`Contract deployed to ${PriceFeeds.target}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
