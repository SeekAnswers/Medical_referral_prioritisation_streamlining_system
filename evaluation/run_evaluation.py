import asyncio
import logging
from evaluation.system_evaluator import FastAPISystemEvaluator

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

async def main():
    """Run comprehensive evaluation"""
    
    print(" FastAPI Medical Referral System - Quantitative Evaluation")
    print("=" * 60)
    
    evaluator = FastAPISystemEvaluator(base_url="http://localhost:8000")
    
    try:
        results = await evaluator.run_comprehensive_evaluation()
        evaluator.print_summary(results)
        return results
    except Exception as e:
        print(f" Evaluation failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(main())