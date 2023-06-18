// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenPriceFeeds {
    AggregatorV3Interface internal ethPriceFeed;
    AggregatorV3Interface internal btcPriceFeed;
    AggregatorV3Interface internal usdcPriceFeed;

    constructor() {
        // Ethereum Price Feed
        ethPriceFeed = AggregatorV3Interface(0x694AA1769357215DE4FAC081bf1f309aDC325306);
        
        // BTC Price Feed
        btcPriceFeed = AggregatorV3Interface(0x1b44F3514812d835EB1BDB0acB33d3fA3351Ee43);
        
        // USDC Price Feed
        usdcPriceFeed = AggregatorV3Interface(0xA2F78ab2355fe2f984D808B5CeE7FD0A93D5270E);
    }

    function getLatestPrices() public view returns (int, int, int) {
        int ethPrice = getLatestPrice(ethPriceFeed);
        int btcPrice = getLatestPrice(btcPriceFeed);
        int usdcPrice = getLatestPrice(usdcPriceFeed);

        return (ethPrice, btcPrice, usdcPrice);
    }

    function getLatestPrice(AggregatorV3Interface priceFeed) internal view returns (int) {
        (
            uint80 roundID,
            int price,
            uint startedAt,
            uint timeStamp,
            uint80 answeredInRound
        ) = priceFeed.latestRoundData();
        
        return price;
    }

    function getNames() public pure returns (string memory, string memory, string memory) {
        return ("Ethereum", "Bitcoin", "USDC");
    }
}