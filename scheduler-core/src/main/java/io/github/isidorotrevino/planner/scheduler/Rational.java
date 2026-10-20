// SPDX-License-Identifier: GPL-3.0-only
package io.github.isidorotrevino.planner.scheduler;

import java.math.BigDecimal;
import java.math.BigInteger;

/** Exact, reduced fractions: scheduling order never depends on rounded scores. */
public record Rational(BigInteger numerator, BigInteger denominator) implements Comparable<Rational> {
  public static final Rational ZERO = of(BigDecimal.ZERO);

  public Rational {
    if (denominator.signum() == 0) throw new IllegalArgumentException("Zero denominator");
    if (denominator.signum() < 0) { numerator = numerator.negate(); denominator = denominator.negate(); }
    var gcd = numerator.gcd(denominator);
    numerator = numerator.divide(gcd);
    denominator = denominator.divide(gcd);
  }

  public static Rational of(BigDecimal number) {
    var value = number.stripTrailingZeros();
    return value.scale() < 0
      ? new Rational(value.unscaledValue().multiply(BigInteger.TEN.pow(-value.scale())), BigInteger.ONE)
      : new Rational(value.unscaledValue(), BigInteger.TEN.pow(value.scale()));
  }

  public Rational add(Rational other) {
    return new Rational(numerator.multiply(other.denominator).add(other.numerator.multiply(denominator)), denominator.multiply(other.denominator));
  }

  public Rational subtract(Rational other) {
    return add(new Rational(other.numerator.negate(), other.denominator));
  }

  public Rational divide(Rational other) {
    return new Rational(numerator.multiply(other.denominator), denominator.multiply(other.numerator));
  }

  @Override public int compareTo(Rational other) {
    return numerator.multiply(other.denominator).compareTo(other.numerator.multiply(denominator));
  }

  @Override public String toString() { return numerator + "/" + denominator; }
}
