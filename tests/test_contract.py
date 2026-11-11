import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from harness.contract import Page,Snapshot
from submission.solution import build

class KnowledgeTests(unittest.TestCase):
    def build_kb(self):
        def page(sid,rate):
            return Page(url='https://example.test/personal/savings-account',title='Savings Account Rates',fetched_at=sid,
                markdown='# Savings Account Rates\n\n| Account Type | Balance Tier | Dividend Rate | Annual Percentage Yield (APY) | Min. to Open | Min. to Earn |\n| --- | --- | --- | --- | --- | --- |\n| Share Savings | $10,000 – $24,999.99 | '+rate+' | '+rate+' | $25 | $10,000 |\n| Share Savings | $25,000+ | 0.50% | 0.50% | $25 | $25,000 |')
        kb=build()
        kb.ingest(Snapshot('01_test','2026-05-01',[page('2026-05-01','0.10%')]))
        kb.ingest(Snapshot('02_test','2026-08-01',[page('2026-08-01','0.15%')]))
        return kb
    def test_qualified_tier(self):
        ans=self.build_kb().answer('What dividend rate is Share Savings with $10,000 balance?')
        self.assertTrue(ans.confident)
        self.assertIn('0.15%',ans.text)
        self.assertNotIn('0.50%',ans.text)
        self.assertEqual(len(ans.sources),1)
    def test_as_of(self):
        ans=self.build_kb().answer('What dividend rate is Share Savings with $10,000 balance?',as_of='2026-05-15')
        self.assertIn('0.10%',ans.text)
        self.assertNotIn('0.15%',ans.text)
    def test_conflict(self):
        cs=self.build_kb().conflicts()
        self.assertTrue(any('0.10%' in x.values and '0.15%' in x.values and x.resolution=='0.15%' for x in cs))
    def test_determinism(self):
        k=self.build_kb()
        a=k.answer('What is the Share Savings APY at $10,000?')
        b=k.answer('What is the Share Savings APY at $10,000?')
        self.assertEqual(a.text,b.text)
        self.assertEqual(a.sources[0].url,b.sources[0].url)
    def test_refusal(self):
        a=self.build_kb().answer('What is the interest rate for a construction loan?')
        self.assertFalse(a.confident)

if __name__=='__main__':unittest.main()
