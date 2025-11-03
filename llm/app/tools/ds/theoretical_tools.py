from typing import Dict, Optional, Annotated
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from app import logger
from app.core.config import settings

class TheoreticalTools:
    """Tools for plotting theoretical distributions"""

    @staticmethod
    @tool("plot_normal_distribution")
    async def plot_normal_distribution(
        mu          : float = 0.0
        , sigma     : float = 1.0
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Plot the normal distribution PDF

        Args:
            mu          : Mean (default: 0.0)
            sigma       : Standard deviation (default: 1.0)
            output_path : Path to save plot

        Returns:
            Dict with plot path
        """
        try:
            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"normal_distribution_mu{mu}_sigma{sigma}.png")

            x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
            y = stats.norm.pdf(x, mu, sigma)

            plt.figure(figsize=(10, 6))
            plt.plot(x, y, 'b-', linewidth=2, label=f'$\mu={mu}$, $\sigma={sigma}$')
            plt.axvline(mu, color='r', linestyle='--', alpha=0.7, label=f'Mean $\mu={mu}$')
            plt.fill_between(x, y, alpha=0.3)
            plt.xlabel('x')
            plt.ylabel('Probability Density')
            plt.title(f'Normal Distribution: $N({mu}, {sigma}^2)$')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"Normal distribution plot saved: {output_path}")

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            return {
                "status"    : 200
                , "message" : "Normal distribution plotted"
                , "data"    : {
                    "plot_path" : output_path
                    , "file_url": file_url
                    , "mu"      : mu
                    , "sigma"   : sigma
                }
            }

        except Exception as e:
            logger.error(f"Error plotting normal distribution: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to plot: {str(e)}"
                , "data"    : None
            }

    @staticmethod
    @tool("plot_distribution")
    async def plot_distribution(
        distribution: str
        , params    : Dict[str, float]
        , output_path: Optional[str] = None
        , state     : Annotated[Dict, InjectedState] = None
    ) -> Dict:
        """
        Plot various theoretical distributions

        Args:
            distribution: Type ('normal', 'binomial', 'poisson', 't', 'chi2', 'exponential')
            params      : Distribution parameters as dict
            output_path : Path to save plot

        Returns:
            Dict with plot path
        """
        try:
            if output_path is None:
                output_dir = Path("output/plots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"{distribution}_distribution.png")

            plt.figure(figsize=(10, 6))

            if distribution == 'normal':
                mu = params.get('mu', 0.0)
                sigma = params.get('sigma', 1.0)
                x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
                y = stats.norm.pdf(x, mu, sigma)
                plt.plot(x, y, linewidth=2)
                plt.title(f'Normal Distribution: $N({mu}, {sigma}^2)$')

            elif distribution == 'binomial':
                n = int(params.get('n', 10))
                p = params.get('p', 0.5)
                x = np.arange(0, n+1)
                y = stats.binom.pmf(x, n, p)
                plt.bar(x, y)
                plt.title(f'Binomial Distribution: $n={n}$, $p={p}$')

            elif distribution == 'poisson':
                lam = params.get('lambda', 5.0)
                x = np.arange(0, int(lam*3))
                y = stats.poisson.pmf(x, lam)
                plt.bar(x, y)
                plt.title(f'Poisson Distribution: $\lambda={lam}$')

            elif distribution == 't':
                df = params.get('df', 10)
                x = np.linspace(-4, 4, 1000)
                y = stats.t.pdf(x, df)
                plt.plot(x, y, linewidth=2)
                plt.title(f"Student's t Distribution: df={df}")

            elif distribution == 'chi2':
                df = params.get('df', 5)
                x = np.linspace(0, df*3, 1000)
                y = stats.chi2.pdf(x, df)
                plt.plot(x, y, linewidth=2)
                plt.title(f'Chi-Squared Distribution: df={df}')

            elif distribution == 'exponential':
                lam = params.get('lambda', 1.0)
                x = np.linspace(0, 5/lam, 1000)
                y = stats.expon.pdf(x, scale=1/lam)
                plt.plot(x, y, linewidth=2)
                plt.title(f'Exponential Distribution: $\lambda={lam}$')

            else:
                return {
                    "status"    : 400
                    , "message" : f"Unknown distribution: {distribution}"
                    , "data"    : None
                }

            plt.xlabel('x')
            plt.ylabel('Probability Density/Mass')
            plt.grid(True, alpha=0.3)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            logger.info(f"{distribution} distribution plot saved: {output_path}")

            filename = Path(output_path).name
            file_url = f"{settings.FRONT_API_BASE_URL}/api/v2/files/plots/{filename}"

            return {
                "status"    : 200
                , "message" : f"{distribution} distribution plotted"
                , "data"    : {
                    "plot_path"     : output_path
                    , "file_url"    : file_url
                    , "distribution": distribution
                    , "params"      : params
                }
            }

        except Exception as e:
            logger.error(f"Error plotting distribution: {str(e)}")
            return {
                "status"    : 500
                , "message" : f"Failed to plot: {str(e)}"
                , "data"    : None
            }
