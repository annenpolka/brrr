# Reduced excerpt of Transaction::calculateOperations on failing_ref
# src/Composer/DependencyResolver/Transaction.php
# aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
# Version / dist-ref / source-ref are the installed identity.
# Abandoned / replacement-package are not that identity.

                        if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
                            $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
                            $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
                        ) {
                            $operations[] = new Operation\UpdateOperation($source, $package);
                        }
