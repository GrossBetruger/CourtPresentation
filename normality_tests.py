import scipy.stats

from matplotlib import pyplot
from scipy.stats import shapiro
from dataclasses import dataclass
from utils import get_engine


@dataclass
class Vendor:
    name: str
    isp: str
    infra: str


def test_normality(data, alpha=0.05, name="sample"):
    statistic, p_value = shapiro(data)
    print(statistic, p_value)
    pyplot.hist(data, bins=len(data) // 2)
    pyplot.title(name)
    pyplot.xlabel("Average Speed")
    pyplot.ylabel("Number of Users")
    pyplot.savefig("normality_" + name +".png")
    pyplot.show()
    pyplot.clf()
    return p_value >= alpha


def get_pure_vendor_users(vendor: Vendor):
    engine = get_engine()
    cursor = engine.cursor()
    cursor.execute(
        """
        select avg(ground_truth_rate) from valid_tests
        where connection = 'LAN'
        and isp = %(isp)s
        and infrastructure = %(infra)s
        and speed = 100
        group by user_name;
        """, {"isp": vendor.isp, "infra": vendor.infra}
    )

    user_averages = []
    for row in cursor.fetchall():
        average, = row
        user_averages.append(average)
    return user_averages


if __name__ == "__main__":
    bezeq = Vendor(name='Bezeq', isp='Bezeq International-Ltd', infra='BEZEQ')
    hot = Vendor(name='HOT', isp='Hot-Net internet services Ltd.', infra='HOT')
    partner = Vendor(name='Partner', isp='Partner Communications Ltd.', infra='PARTNER')

    for vend in [bezeq, hot]:
        user_averages = get_pure_vendor_users(vend)
        print(f"{vend.name}: sample is coming from a normal distribution: {test_normality(user_averages, name=vend.name)}")

    random_results = scipy.stats.norm.rvs(loc=5, scale=3, size=100)
    bi_modal = [10] * 5 + [100] * 5
    print(f"Random sample is coming from a normal distribution: {test_normality(random_results)}")
    print(f"Bimodal sample is coming from a normal distribution: {test_normality(bi_modal)}")
