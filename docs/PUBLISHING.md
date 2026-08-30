# Publishing the repository

The plan: this repository stays **private** as the working archive. The public
artifact repository is a **new repository with a single clean commit**, created from
this one's final working tree.

## Why a fresh repository

Git keeps every version of every file forever, and `git clone` downloads the whole
history. Deleting a file only changes what is visible at the tip — every earlier
commit still contains it, and anyone who clones a public repo can retrieve it:

```bash
git show 0b40757:explore/hi_individual/hi_explain_H1.png | wc -c   # still there
```

The per-child hearing-impairment figures were individual-level participant outputs
and must not be published. A fresh repository leaves them behind entirely, along
with the development archaeology that would otherwise be part of the public record:
the `"Update fmt.Println to print 'Goodbye World'"` commit, the stray `git push` in a
merge message, and roughly twenty near-identical run-log commits from August.

A paper's artifact repository is a deliverable, not a lab notebook.

## Do this LAST

Everything else on `docs/PUBLICATION_CHECKLIST.md` should be finished here first —
the TODO placeholders, the TRIPOD+AI checklist, the v1/v2 figure decision. Whatever
is in the working tree at that moment becomes the public repository's first commit.

The only exception is the DOI, which does not exist until after publishing. See
step 6.

---

## Step 1 — finish and push everything here

```bash
cd /work/dld-ml-screening
git status          # clean
git push
```

## Step 2 — export a clean copy of the tracked files

`git archive` writes out exactly the tracked files at HEAD: no `.git`, no untracked
scratch files, no ignored data.

```bash
mkdir -p /work/dld-publish
git archive HEAD | tar -x -C /work/dld-publish
cd /work/dld-publish
ls -a               # no .git directory
```

## Step 3 — verify before it becomes public

Each of these must print nothing.

```bash
find . -iname "*.xlsx" -o -iname "*.xls"          # no spreadsheets
find . -path "*hi_individual*"                     # no per-child figures
find . -name "hi_scores.csv" -o -name "hi_attributions_long.csv"
find . -name "hi_probe_scores.csv"
ls data/                                           # must show ONLY README.md
```

And check for leftover placeholders — every one must be filled or deliberately kept:

```bash
grep -rn "TODO" README.md LICENSE CITATION.cff data/README.md
```

Then open `results/oof_predictions.csv` and confirm it still has only `y_true` and
`oof_prob`, with no identifier column.

## Step 4 — create the public repository

The original working repository has been renamed to `dld-ml-screening-archive`, which
frees the name `dld-ml-screening` for the published one. `CITATION.cff` already points
at that URL.

On GitHub: **New repository** → name `dld-ml-screening` → **Private** for now →
**no** README, **no** .gitignore, **no** licence (the export already has all three)
→ Create repository.

Create it private and flip it to public later rather than making two repositories.
GitHub changes visibility with a single toggle (Settings → General → Danger Zone →
Change visibility), so you can push the clean commit, read the repository over as a
stranger would, and only then publish — same repository, same URL, nothing to migrate.

Review for this submission is **single-blind** — reviewers see the authors — so no
anonymised view or anonymised Zenodo upload is needed. Once public, the URL goes
straight into the Data Availability Statement.

## Step 5 — one clean commit, then push

```bash
cd /work/dld-publish
git init -b main
git add -A
git status                    # last look at exactly what becomes public

git commit -m "Analysis code, results and documentation for Esbensen, Andersen & Morini (2026)

Interpretable machine-learning screening for developmental language disorder
in Danish children. Model development with internal validation only.

The individual-level data are not distributed; see data/README.md for what is
openly available instead."

git remote add origin https://github.com/elisabethan2/dld-ml-screening.git
git push -u origin main
```

You will be prompted for credentials: username `Elisabethan2`, password = a
fine-grained personal access token with **Contents: Read and write** on the new
repository.

## Step 6 — make it public, then archive on Zenodo for the DOI

Read the repository over on GitHub first — the README as a stranger sees it, the file
tree, `data/README.md`. Then Settings → General → Danger Zone → **Change visibility →
Public**.

Zenodo can only archive a **public** repository, so this has to come first.

1. Sign in to <https://zenodo.org> with your GitHub account
2. Go to your Zenodo GitHub settings and switch **on** the toggle for the new repository
3. Back on GitHub: **Releases → Create a new release**, tag `v1.0.0`, publish it
4. Zenodo mints a DOI automatically within a few minutes

Zenodo gives you two DOIs. Use the **concept DOI** (the "all versions" one) in the
paper, `README.md` and `CITATION.cff` — it always resolves to the newest version, so
you do not have to update the paper if you later release a v1.0.1. The
version-specific DOI is for citing one exact snapshot.

Then fill the DOI into `README.md` and `CITATION.cff`, commit, and push. That commit
does not need a new release.

## Step 7 — finish up

- Put the repository URL and concept DOI into the paper's Data Availability Statement,
  replacing `[repository URL / DOI]`
- Keep this private repository as the working archive — do not delete it
- Delete `/work/dld-publish` once the push has succeeded, or keep it as the clone you
  work in from now on

## If you later need to change the published repository

Work in the public repository normally from then on — ordinary commits, no rewriting.
The point of the fresh start was the history before it, not a permanent freeze.
