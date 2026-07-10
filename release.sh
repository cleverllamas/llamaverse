#!/bin/bash
set -e

VERSION="${1:-2.0}"
PRIVATE_DIR="/home/david/work/cl2/llamaverse/private/llamaverse-internal"
PUBLIC_DIR="/home/david/work/cl2/llamaverse/public/llamaverse"

echo "🦙 Llamaverse Release: $VERSION"
echo ""

# Step 1: Tag private repo
echo "Step 1: Tagging private repo as $VERSION..."
cd "$PRIVATE_DIR"
git tag -a "$VERSION" -m "Release version $VERSION"
git push origin "$VERSION"
echo "✓ Tagged private repo"

# Step 2: Copy private HEAD to public local (overwrite, exclude internal files)
echo ""
echo "Step 2: Copying private HEAD to public local repo (cleaned)..."
cd "$PUBLIC_DIR"
git fetch origin
git reset --hard origin/main
git clean -fd

# Copy all files from private to public, excluding internal-only files
rsync -av --delete "$PRIVATE_DIR/" "$PUBLIC_DIR/" \
  --exclude='.git' \
  --exclude='*.py' \
  --exclude='gradle.properties' \
  --exclude='gradle-ml12.properties' \
  --exclude='build' \
  --exclude='.gradle' \
  --exclude='gradlew' \
  --exclude='gradlew.bat'
echo "✓ Copied private HEAD to public (internal files excluded)"

# Step 3: Remove any remaining internal-only files from public working directory
echo ""
echo "Step 3: Final cleanup of internal-only files..."
rm -f "$PUBLIC_DIR"/*.py "$PUBLIC_DIR"/gradle*.properties "$PUBLIC_DIR"/gradlew "$PUBLIC_DIR"/gradlew.bat 2>/dev/null || true
rm -rf "$PUBLIC_DIR"/build "$PUBLIC_DIR"/.gradle "$PUBLIC_DIR"/gradle 2>/dev/null || true
echo "✓ Internal files removed"

# Step 4: Commit cleaned version to public local
echo ""
echo "Step 4: Committing cleaned version to public local..."
cd "$PUBLIC_DIR"
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Release version $VERSION from private repo (cleaned)"
else
  echo "No changes to commit"
fi
echo "✓ Committed"

# Step 5: Tag the release in public local
echo ""
echo "Step 5: Tagging version $VERSION in public repo..."
git tag -a "$VERSION" -m "Release version $VERSION" 2>/dev/null || echo "Tag already exists, overwriting..." && git tag -d "$VERSION" && git tag -a "$VERSION" -m "Release version $VERSION"
echo "✓ Tagged"

# Step 6: Push to public remote
echo ""
echo "Step 6: Pushing main and tag to public remote..."
git push origin main --force
git push origin "$VERSION"
echo "✓ Pushed to public remote"

# Step 7: Create GitHub release
echo ""
echo "Step 7: Creating GitHub release..."
gh release create "$VERSION" --generate-notes
echo "✓ Release created on GitHub"

echo ""
echo "🎉 Release $VERSION complete!"
