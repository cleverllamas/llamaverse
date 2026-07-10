# Llamaverse Release Process (Version 2.0+)

## Overview
Releases follow a clean private-to-public workflow where internal files are filtered out:
1. **Private repo** (source): Includes all internal tooling and development files
2. **Public repo** (published): Synced from private HEAD with internal-only files removed

## Files Excluded from Public Releases
- Python scripts: `*.py` (internal data generation and setup tools)
- Gradle properties: `gradle.properties`, `gradle-ml12.properties` (contain secrets)
- Build artifacts: `build/`, `.gradle/` directories  
- Build scripts: `gradlew`, `gradlew.bat`
- Gradle config: `gradle/` directory

## Required Public README Content
For every public release, `README.md` must be exactly:

`For information about this repo, plesae visit https://cleverllamas.com/articles/llamaverse`

## Prerequisites
- Private repo has all changes committed and pushed
- Public repo local checkout exists at `../../public/llamaverse`
- `rsync` is installed
- GitHub CLI (`gh`) is installed and authenticated

## Quick Start: Automated Release

```bash
cd /home/david/work/cl2/llamaverse/private/llamaverse-internal
./release.sh 2.0
```

The script automates all steps below.

## Manual Release Steps

### Step 1: Tag the Private Repo
```bash
cd /home/david/work/cl2/llamaverse/private/llamaverse-internal
git tag -a 2.0 -m "Release version 2.0"
git push origin 2.0
```

### Step 2: Copy Private HEAD to Public Local (Cleaned)
```bash
cd /home/david/work/cl2/llamaverse/public/llamaverse
git fetch origin
git reset --hard origin/main
git clean -fd

# Copy from private, excluding internal files
rsync -av --delete /home/david/work/cl2/llamaverse/private/llamaverse-internal/ . \
  --exclude='.git' \
  --exclude='*.py' \
  --exclude='gradle.properties' \
  --exclude='gradle-ml12.properties' \
  --exclude='build' \
  --exclude='.gradle' \
  --exclude='gradlew' \
  --exclude='gradlew.bat'

# Final cleanup
rm -f *.py gradle*.properties gradlew gradlew.bat
rm -rf build .gradle gradle

# Force README to canonical public text
cat > README.md <<'EOF'
For information about this repo, plesae visit https://cleverllamas.com/articles/llamaverse
EOF
```

### Step 3: Commit Cleaned Version
```bash
git add -A
git commit -m "Release version 2.0 from private repo (cleaned)"
git tag -a 2.0 -m "Release version 2.0"
```

### Step 4: Push to Public Remote
```bash
git push origin main --force
git push origin 2.0
```

### Step 5: Create GitHub Release
```bash
gh release create 2.0 --generate-notes
```

## Verification

After release, verify everything is clean and correct:

```bash
# Check private repo has tag
cd /home/david/work/cl2/llamaverse/private/llamaverse-internal
git tag -l | grep 2.0

# Check public repo is clean (no Python files, no gradle.properties)
cd /home/david/work/cl2/llamaverse/public/llamaverse
ls -la | grep -E "\.py|gradle\.properties"  # Should return nothing
find . -name "gradle.properties" -o -name "*.py"  # Should return nothing

# Verify tags and commits
git log -1 --oneline
git tag -l | grep 2.0

# Check GitHub release exists
gh release view 2.0
```

## Notes
- Private repo remains the source of truth with all internal development tools
- Public repo is a curated, cleaned copy specifically for public releases
- Internal files are permanently excluded from public GitHub
- Each release is explicitly cleaned locally before pushing to public
- Use `--force` push to ensure public main branch stays synchronized
