# Interactive plot browser

You can publish your plots to a personal, interactive web browser using the
[CMS Common Analysis Tools plot browser](https://cms-analysis.docs.cern.ch/guidelines/other/plot_browser/#install-the-plot-browser).

The page above has detailed, illustrated instructions. After submitting the form to register a
personal website you can adjust some settings (e.g. enabling **Use .htaccess files**).

!!! important "Share your EOS space with `wwweos`"
    Your EOS user-space directory must be shared with the `wwweos` account, as described in the
    instructions, before the browser becomes available.

Once the browser is set up, deploy a directory of plots with:

```sh
python3 /eos/user/u/username/php-plots/bin/pb_deploy_plots.py \
  /path/to/your/plots/ \
  /eos/user/u/username/php-plots/<target-directory>/ \
  --recursive --pdf-to-png
```

Notes:

- `--pdf-to-png` makes a `.png` copy of each `.pdf` plot.
- `/eos/user/u/username/` is **your** EOS area (`/u/username` here is just a placeholder).
- `/eos/user/u/username/php-plots/` is where you cloned the plot-browser repository
  (`cms-analysis/general/php-plots`).
