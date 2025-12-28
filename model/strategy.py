def get_public_debt_allocation():
    # Get 20y vertex rate value
    long_term_rate = 6.9 / 100

    # inflation_allocation = 18.75 * long_term_rate - 0.75
    # floating_allocation = 1.0 - inflation_allocation

    inflation_allocation = 22.5 * long_term_rate - 0.90
    floating_allocation = 1.0 - inflation_allocation

    return [floating_allocation, inflation_allocation, 0.0]
