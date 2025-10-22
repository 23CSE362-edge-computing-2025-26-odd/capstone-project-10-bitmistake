# Post-Fix Checklist

## Before Running

- [ ] All files saved and changes applied
- [ ] No syntax errors (run `python -m py_compile src/*.py`)
- [ ] Backup of old results (if any)

## Running the Fixed Version

- [ ] Run: `python run_fixed_comparison.py`
  - OR manually: `python main.py hospital`
- [ ] Watch for ERROR messages in console
- [ ] Verify "COMPARISON COMPLETED" message appears
- [ ] Check that summary table is printed

## Validation

- [ ] Run: `python test_fixes.py`
- [ ] All 6 tests should pass
- [ ] No "FAIL" messages in output
- [ ] Check for any WARNING messages

## Results Verification

### Files Created
- [ ] `data/hospital_comparison_results.json` exists
- [ ] `reports/hospital_comparison_report.html` exists
- [ ] `plots/` directory has 9+ PNG files
- [ ] `logs/metrics_.log` has recent timestamp

### Data Quality
- [ ] Open `data/hospital_comparison_results.json`
- [ ] Check `total_runs` is > 0
- [ ] Verify 5-6 algorithms listed
- [ ] Confirm 3 scenarios present
- [ ] Each scenario has results for each algorithm

### Visualizations
- [ ] Open `plots/comparison_latency.png`
  - Should show bars of different heights
  - FNPA should be shortest (best)
- [ ] Open `plots/comparison_energy.png`
  - FNPA should be lower than others
- [ ] Open `plots/comparison_load_balance.png`
  - FNPA should be at 1.0
- [ ] Open `plots/latency_distribution_boxplot.png`
  - Should show boxes with whiskers
  - Different distributions per algorithm
- [ ] Check timeline charts exist (3 files)
- [ ] Check heatmap exists and has colors

## Expected Behavior

### Console Output Should Show:
- [x] "Creating comparison charts for X algorithms"
- [x] "DEBUG" messages showing data being processed
- [x] Summary table with algorithm metrics
- [x] "All visualizations generated in plots/"
- [x] No "ERROR" messages (warnings OK)

### Metrics Should Show:
- [x] FNPA has lowest latency (~800ms)
- [x] Other algorithms vary (1600-1900ms)
- [x] FNPA has lowest energy (~40J)
- [x] FNPA has perfect load balance (1.0)
- [x] No two algorithms are identical

### If Predictive Algorithm:
- [x] Either excluded (if no models)
- [x] Or different from OLB (if models present)
- [x] Warning message if disabled

## Troubleshooting

### If tests fail:
1. Check which specific test failed
2. Review error message
3. Check `logs/metrics_.log` for details
4. Verify comparison completed successfully

### If visualizations are wrong:
1. Delete `plots/` directory
2. Delete `data/hospital_comparison_results.json`
3. Run comparison again
4. Check for ERROR messages

### If algorithms still identical:
1. Verify fixes were applied: `git diff src/`
2. Check console for "DEBUG" messages
3. Run `python test_fixes.py` test 2
4. Review `VISUALIZATION_ISSUES_ANALYSIS.md`

## Success Criteria

✅ **All checks passed if:**
- Comparison completes without errors
- Test suite passes all 6 tests
- Visualizations show varied values
- FNPA performs best (lowest latency)
- No duplicate algorithms (unless Predictive disabled)
- All 9+ visualization files created

## Next Actions

After successful validation:
- [ ] Review visualizations in detail
- [ ] Check HTML report
- [ ] Analyze per-task data in logs
- [ ] Compare with previous results (if any)
- [ ] Document any interesting findings

## If Issues Persist

1. **Check logs:**
   ```bash
   cat logs/metrics_.log | grep ERROR
   ```

2. **Validate data structure:**
   ```bash
   python -c "import json; print(json.load(open('data/hospital_comparison_results.json'))['total_runs'])"
   ```

3. **Test individual algorithm:**
   ```bash
   python main.py olb  # Test OLB alone
   ```

4. **Review documentation:**
   - `README_FIXES.md` - Complete overview
   - `QUICK_START.md` - Quick reference
   - `FIXES_APPLIED.md` - Detailed fixes
   - `VISUALIZATION_ISSUES_ANALYSIS.md` - Root causes

## Contact/Support

If all else fails:
- Review all ERROR messages in console
- Check `logs/metrics_.log` for stack traces
- Verify Python environment and dependencies
- Check YAFS installation
- Review algorithm implementations

---

**Last Updated:** After applying all fixes
**Status:** Ready to run
**Command:** `python run_fixed_comparison.py`
