import logging
from typing import Any, Dict, List

import defi.dao_cross.optimize as ddacropt
import defi.dao_cross.order as ddacrord
import helpers.hdbg as hdbg
import helpers.hprint as hprint
import helpers.hunit_test as hunitest

_LOG = logging.getLogger(__name__)


def _generate_test_orders(
    base_tokens: List[str],
    quote_tokens: List[str],
    actions: List[str],
    quantities: List[float],
    limit_prices: List[float],
) -> List[ddacrord.Order]:
    """
    Create N `Order` instances using the inputs.

    See `Order` for params description.
    """
    # Use dummy values as the params are not relevant for the
    # optimization problem.
    timestamp = None
    deposit_address = 1
    wallet_address = 1
    orders: List[ddacrord.Order] = []
    # TODO(Grisha): check that all lists are of the same length.
    for i in range(len(base_tokens)):
        order_i = ddacrord.Order(
            base_tokens[i],
            quote_tokens[i],
            actions[i],
            quantities[i],
            limit_prices[i],
            timestamp,
            deposit_address,
            wallet_address,
        )
        orders.append(order_i)
    return orders


def _check(
    self_: Any,
    orders: List[ddacrord.Order],
    prices: Dict[str, float],
    expected_volume: float,
    expected_quantities: str,
) -> None:
    """
    Check that the optimization problem is correctly solved.

    :param orders: `Order` instances
    :param prices: prices in terms of a reference common currency (e.g., USDT)
        for each token
    :param expected_volume: optimization objective: the total executed volume
    :param expected_quantities: executed quantity for each order, e.g.,
        "(4) 2.0 6.0 7.0 1.0"
    """
    result = ddacropt.run_solver(orders, prices)
    # Check that a solution is found.
    self_.assertEqual(result["problem_objective_value"], expected_volume)
    # Freeze the executed quantity values.
    var_values_str = hprint.format_list(result["q_base_asterisk"])
    self_.assert_equal(var_values_str, expected_quantities, fuzzy_match=True)


# TODO(Grisha): finish the tests.
class TestRunSolver1(hunitest.TestCase):
    """
    Run the optimization problem for 2 orders with the same base token.
    """

    _base_tokens = ["BTC", "BTC"]
    _quote_tokens = ["ETH", "ETH"]
    _actions = ["buy", "sell"]
    _quantities = [8, 9]

    def test1(self) -> None:
        """
        The limit price condition is True for all orders.
        """
        # Get inputs.
        prices = {"BTC": 2, "ETH": 4}
        limit_prices = [3, 1]
        test_orders = _generate_test_orders(
            self._base_tokens,
            self._quote_tokens,
            self._actions,
            self._quantities,
            limit_prices,
        )
        # Run the check.
        expected_volume = 32
        expected_quantities = "(2) 8.0 8.0"
        _check(self, test_orders, prices, expected_volume, expected_quantities)

    def test2(self) -> None:
        """
        The limit price condition is False for a buy order and True for the
        sell order.
        """

    def test3(self) -> None:
        """
        The limit price condition is False for a sell order and True for the
        buy order.
        """


# TODO(Grisha): finish the tests.
class TestRunSolver2(hunitest.TestCase):
    """
    Run the optimization problem for N orders with the same base token.
    """

    _base_tokens = ["BTC", "BTC", "BTC", "BTC"]
    _quote_tokens = ["ETH", "ETH", "ETH", "ETH"]
    _actions = ["buy", "buy", "sell", "sell"]
    _quantities = [2, 6, 7, 5]

    def test1(self) -> None:
        """
        The limit price condition is True for all orders.
        """
        # Get inputs.
        prices = {"BTC": 2, "ETH": 8}
        limit_prices = [4, 4.5, 2.1, 3]
        test_orders = _generate_test_orders(
            self._base_tokens,
            self._quote_tokens,
            self._actions,
            self._quantities,
            limit_prices,
        )
        # Run the check.
        expected_volume = 32
        expected_quantities = "(4) 2.0 6.0 7.0 1.0"
        _check(self, test_orders, prices, expected_volume, expected_quantities)

    def test2(self) -> None:
        """
        The limit price condition is False for one buy order and is True for
        the rest of the orders.
        """

    def test3(self) -> None:
        """
        The limit price condition is False for one sell order and is True for
        the rest of the orders.
        """


# TODO(Grisha): finish the tests.
class TestRunSolver3(hunitest.TestCase):
    """
    Run the optimization problem for N orders with different base tokens.
    """

    _base_tokens = ["BTC", "BTC", "BTC", "BTC", "ETH", "ETH", "ETH", "ETH"]
    _quote_tokens = ["ETH", "ETH", "ETH", "ETH", "BTC", "BTC", "BTC", "BTC"]
    _actions = ["buy", "buy", "sell", "sell", "buy", "buy", "sell", "sell"]
    _quantities = [4, 2, 5, 3, 6, 2, 9, 1]

    def test1(self) -> None:
        """
        The limit price condition is True for all orders.
        """
        # Get inputs.
        prices = {"BTC": 3, "ETH": 6}
        limit_prices = [3, 3.5, 1.5, 1.9, 0.6, 2, 0.1, 0.25]
        test_orders = _generate_test_orders(
            self._base_tokens,
            self._quote_tokens,
            self._actions,
            self._quantities,
            limit_prices,
        )
        # Run the check.
        expected_volume = 132
        expected_quantities = "(8) 4.0 2.0 5.0 1.0 6.0 2.0 8.0 0.0"
        _check(self, test_orders, prices, expected_volume, expected_quantities)

    def test2(self) -> None:
        """
        The limit price condition is False for one buy order and is True for
        the rest of the orders for each base token.
        """

    def test3(self) -> None:
        """
        The limit price condition is False for one sell order and is True for
        the rest of the orders for each base.
        """


# TODO(Grisha): replace with the class that tests for N random orders.
# TODO(Grisha): use `_generate_test_orders()` to get the orders.
class TestRunSolver4(hunitest.TestCase):
    """
    Run the solver using toy orders.
    """

    @staticmethod
    def get_test_btc_orders(
        limit_prices: List[float],
    ) -> List[ddacrord.Order]:
        """
        Get toy BTC orders for the unit tests.

        :param limit_prices: limit in prices: quote token per base token
        :return: buy and sell orders with the base token "BTC"
        """
        hdbg.dassert_eq(len(limit_prices), 4)
        # Set the common variables.
        base_token = "BTC"
        quote_token = "ETH"
        buy_action = "buy"
        sell_action = "sell"
        timestamp = None
        deposit_address = 1
        wallet_address = 1
        # Genereate buy orders.
        quantity = 4
        order_0 = ddacrord.Order(
            base_token,
            quote_token,
            buy_action,
            quantity,
            limit_prices[0],
            timestamp,
            deposit_address,
            wallet_address,
        )
        #
        quantity = 5
        order_1 = ddacrord.Order(
            base_token,
            quote_token,
            buy_action,
            quantity,
            limit_prices[1],
            timestamp,
            deposit_address,
            wallet_address,
        )
        # Genereate sell orders.
        quantity = 6
        order_2 = ddacrord.Order(
            base_token,
            quote_token,
            sell_action,
            quantity,
            limit_prices[2],
            timestamp,
            deposit_address,
            wallet_address,
        )
        #
        quantity = 2
        order_3 = ddacrord.Order(
            base_token,
            quote_token,
            sell_action,
            quantity,
            limit_prices[3],
            timestamp,
            deposit_address,
            wallet_address,
        )
        orders = [order_0, order_1, order_2, order_3]
        return orders

    @staticmethod
    def get_test_eth_orders(
        limit_prices: List[float],
    ) -> List[ddacrord.Order]:
        """
        Get toy ETH orders for the unit tests.

        :param limit_prices: limit in prices: quote token per base token
        :return: buy and sell orders with the base token "ETH"
        """
        hdbg.dassert_eq(len(limit_prices), 4)
        # Set the common variables.
        base_token = "ETH"
        quote_token = "BTC"
        buy_action = "buy"
        sell_action = "sell"
        timestamp = None
        deposit_address = 1
        wallet_address = 1
        # Genereate buy orders.
        quantity = 1
        order_0 = ddacrord.Order(
            base_token,
            quote_token,
            buy_action,
            quantity,
            limit_prices[0],
            timestamp,
            deposit_address,
            wallet_address,
        )
        #
        quantity = 9
        order_1 = ddacrord.Order(
            base_token,
            quote_token,
            buy_action,
            quantity,
            limit_prices[1],
            timestamp,
            deposit_address,
            wallet_address,
        )
        # Genereate sell orders.
        quantity = 8
        order_2 = ddacrord.Order(
            base_token,
            quote_token,
            sell_action,
            quantity,
            limit_prices[2],
            timestamp,
            deposit_address,
            wallet_address,
        )
        #
        quantity = 6
        order_3 = ddacrord.Order(
            base_token,
            quote_token,
            sell_action,
            quantity,
            limit_prices[3],
            timestamp,
            deposit_address,
            wallet_address,
        )
        orders = [order_0, order_1, order_2, order_3]
        return orders

    def test1(self) -> None:
        """
        The limit price condition is True for all orders.
        """
        # All the limit prices >= clearing price for the buy orders
        # <= clearing price for the sell orders.
        btc_limit_prices = [5, 5.5, 3, 2]
        btc_orders = self.get_test_btc_orders(btc_limit_prices)
        eth_limit_prices = [0.3, 0.43, 0.1, 0.2]
        eth_orders = self.get_test_eth_orders(eth_limit_prices)
        # Run the check.
        orders = btc_orders + eth_orders
        prices = {"BTC": 2, "ETH": 8}
        expected_volume = 192
        expected_quantities = "(8) 3.0 5.0 6.0 2.0 1.0 9.0 8.0 2.0"
        _check(self, orders, prices, expected_volume, expected_quantities)

    def test2(self) -> None:
        """
        The limit price condition is False for a buy order.
        """
        prices = {"BTC": 2, "ETH": 8}
        btc_limit_prices = [5, 2, 3, 2]
        btc_orders = self.get_test_btc_orders(btc_limit_prices)
        # Run the check.
        expected_volume = 16
        expected_quantities = "(4) 4.0 0.0 4.0 0.0"
        _check(self, btc_orders, prices, expected_volume, expected_quantities)

    def test3(self) -> None:
        """
        The limit price condition is False for a sell order.
        """
        prices = {"BTC": 2, "ETH": 8}
        btc_limit_prices = [5, 5.5, 3, 6]
        btc_orders = self.get_test_btc_orders(btc_limit_prices)
        # Run the check.
        expected_volume = 24
        expected_quantities = "(4) 1.0 5.0 6.0 0.0"
        _check(self, btc_orders, prices, expected_volume, expected_quantities)
