from app.agents.supervisor import SupervisorAgent
import pandas as pd

companies = pd.read_csv("data/saudi_companies.csv", dtype={"symbol": str})

agent = SupervisorAgent()

for symbol in companies["symbol"]:
    symbol = str(symbol).replace(".0", "").strip()

    report = agent.run(
        symbol=symbol,
        save=True,
    )

    print(
        symbol,
        report["recommendation"],
        report["final_score"],
    )