from abc import ABCMeta
from datetime import datetime

from rate import BondRate, FixedRate, CDIRate, SELICRate, IPCARate


"""
A security is a tradable financial asset of any kind.
Securities are broadly categorized into:
- debt securities (e.g., banknotes, bonds and debentures)
- equity securities (e.g., common stocks)
- derivative securities (e.g., forwards, futures, options and swaps)
Reference: http://en.wikipedia.org/wiki/Security_(finance)

Fund shares may be categorized as equity securities as well.
"""


class Security:
    __metaclass__ = ABCMeta

    def __init__(self, name, issuer=""):
        self.name = name
        self.issuer = issuer


#####################
# EQUITY SECURITIES #
#####################

class EquitySecurity(Security):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        Security.__init__(self, name)

    @staticmethod
    def create(name):
        if name.endswith("F"):
            name = name[:-1]
        if name.endswith("11"):
            return StockUnit(name)
        else:
            return Stock(name)


##########
# Stocks #
##########

class Stock(EquitySecurity):
    def __init__(self, name):
        code = int(name[-1])
        assert code >= 3 and code <= 8, "Invalid stock: %s" % name
        EquitySecurity.__init__(self, name)


class StockUnit(EquitySecurity):
    def __init__(self, name):
        assert name.endswith("11")
        EquitySecurity.__init__(self, name)


class SubscriptionRight(EquitySecurity):
    def __init__(self, name, stock):
        code = int(name[-1])
        assert code == 1 or code == 2
        self.stock = stock
        EquitySecurity.__init__(self, name)


##########################
# Investment Fund Shares #
##########################

class FundShare(EquitySecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name):
        EquitySecurity.__init__(self, name)


class MutualFundShare(FundShare):
    pass


class ExchangeTradedFundShare(FundShare):
    pass


class HedgeFundShare(FundShare):
    pass


class RealEstateFundShare(FundShare):
    def __init__(self, name):
        assert name.endswith("11") or name.endswith("11B")
        FundShare.__init__(self, name)


###################
# DEBT SECURITIES #
###################

class DebtSecurity(Security):
    __metaclass__ = ABCMeta

    def __init__(self, name, maturity, rate):
        Security.__init__(self, name)
        self.maturity = maturity
        assert isinstance(rate, BondRate)
        self.rate = rate

    def is_expired(self):
        return self.maturity < datetime.now()


##################
# Treasure Bonds #
##################

class TreasureBond(DebtSecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name, rate):
        maturity = datetime.strptime(name[-6:], "%d%m%y")
        DebtSecurity.__init__(self, name, maturity, rate)
        self.issuer = "Tesouro Nacional"

    @staticmethod
    def create(name, rate_value):
        if name.startswith("LTN_"):
            return LTN(name, rate_value)
        elif name.startswith("LFT_"):
            return LFT(name, rate_value)
        elif name.startswith("NTN-F_"):
            return NTNF(name, rate_value)
        elif name.startswith("NTN-B_Principal_"):
            return NTNBP(name, rate_value)
        elif name.startswith("NTN-B_"):
            return NTNB(name, rate_value)
        else:
            raise Exception("Invalid Treasure Bond!")


class LTN(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("LTN_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)


class LFT(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("LFT_")
        rate = SELICRate(rate_value)
        TreasureBond.__init__(self, name, rate)


class NTNF(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("NTN-F_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)


class NTNB(TreasureBond):
    def __init__(self, name, rate_value):
        assert (name.startswith("NTN-B_") and
                not name.startswith("NTN-B_Principal_"))
        rate = IPCARate(rate_value)
        TreasureBond.__init__(self, name, rate)


class NTNBP(TreasureBond):
    def __init__(self, name, rate_value):
        assert name.startswith("NTN-B_Principal_")
        rate = FixedRate(rate_value)
        TreasureBond.__init__(self, name, rate)


#############
# Bank Bond #
#############

class BankBond(DebtSecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name, maturity, rate, issue_date):
        DebtSecurity.__init__(self, name, maturity, rate)
        self.issue_date = issue_date


class LCI(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date):
        assert name.startswith("LCI")
        rate = CDIRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date)


class CDB(BankBond):
    def __init__(self, name, maturity, rate_value, issue_date):
        assert name.startswith("CDB")
        rate = CDIRate(rate_value)
        BankBond.__init__(self, name, maturity, rate, issue_date)


##############
# Debentures #
##############

class Debenture(DebtSecurity):
    __metaclass__ = ABCMeta

    def __init__(self, name, maturity, rate_value):
        rate = IPCARate(rate_value)
        DebtSecurity.__init__(self, name, maturity, rate)


class RegularDebenture(Debenture):
    def __init__(self, name, maturity, rate_value):
        Debenture.__init__(self, name, maturity, rate_value)


class InfraDebenture(Debenture):
    def __init__(self, name, maturity, rate_value):
        Debenture.__init__(self, name, maturity, rate_value)


#########################
# DERIVATIVE SECURITIES #
#########################

class DerivativeSecurity(Security):
    __metaclass__ = ABCMeta


class Forward(DerivativeSecurity):
    pass


class Future(DerivativeSecurity):
    pass


class Option(DerivativeSecurity):
    pass


class Swap(DerivativeSecurity):
    pass
